#!/usr/bin/env python3
"""
GitHub Integration for Grok Engine
- Pull findings into repo
- Monitor PRs for vulns
- Create issues for findings
- Auto-push changes

OLLAMA CLOUD ONLY — No expensive APIs
"""

import os
import subprocess
import json
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime

try:
    import requests
except ImportError:
    requests = None

class GithubIntegration:
    def __init__(self, config: Dict):
        self.config = config
        self.owner = config["owner"]
        self.repo = config["repo"]
        self.token = config["token"] or os.environ.get("GITHUB_TOKEN", "")
        self.url = config["url"]
        self.api_base = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
        
    def get_latest_commits(self, limit: int = 10) -> List[Dict]:
        """Fetch latest commits"""
        if not requests:
            return []
        
        try:
            resp = requests.get(
                f"{self.api_base}/repos/{self.owner}/{self.repo}/commits",
                headers=self.headers,
                params={"per_page": limit}
            )
            return resp.json() if resp.status_code == 200 else []
        except Exception as e:
            print(f"❌ Get commits error: {e}")
            return []
    
    def get_open_prs(self) -> List[Dict]:
        """Fetch open PRs"""
        if not requests:
            return []
        
        try:
            resp = requests.get(
                f"{self.api_base}/repos/{self.owner}/{self.repo}/pulls",
                headers=self.headers,
                params={"state": "open"}
            )
            return resp.json() if resp.status_code == 200 else []
        except Exception as e:
            print(f"❌ Get PRs error: {e}")
            return []
    
    def create_issue(self, title: str, body: str, labels: List[str] = None) -> Optional[Dict]:
        """Create a GitHub issue"""
        if not requests or not self.token:
            print("⚠️  GitHub token not set. Skipping issue creation.")
            return None
        
        try:
            data = {
                "title": title,
                "body": body,
                "labels": labels or ["grok-finding"],
            }
            resp = requests.post(
                f"{self.api_base}/repos/{self.owner}/{self.repo}/issues",
                headers=self.headers,
                json=data
            )
            return resp.json() if resp.status_code == 201 else None
        except Exception as e:
            print(f"❌ Create issue error: {e}")
            return None
    
    def push_findings(self, findings_file: Path) -> bool:
        """Push findings JSON to repo"""
        try:
            # git add findings.json && git commit && git push
            subprocess.run(
                ["git", "add", str(findings_file)],
                cwd=self.config.get("grok_subdir", "."),
                check=True
            )
            subprocess.run(
                ["git", "commit", "-m", f"[Grok] Add findings - {datetime.now().isoformat()}"],
                cwd=self.config.get("grok_subdir", "."),
                check=True
            )
            subprocess.run(
                ["git", "push", "origin", self.config["branch"]],
                cwd=self.config.get("grok_subdir", "."),
                check=True
            )
            print(f"✅ Pushed findings to {self.url}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Push error: {e}")
            return False

def init_github(config: Dict) -> GithubIntegration:
    """Initialize GitHub integration"""
    if not config.get("enabled"):
        return None
    
    github = GithubIntegration(config)
    print(f"✅ GitHub integration ready: {github.url}")
    return github
