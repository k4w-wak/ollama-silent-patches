"""Grok Git Integration — Git commands from Grok.
Ported from claw-code git tools.
"""
import subprocess
import os
from pathlib import Path
from datetime import datetime

def git_init(repo_path: str = "") -> str:
    """Initialize a git repository. Input: path (empty = current dir)"""
    path = repo_path.strip() or os.getcwd()
    try:
        r = subprocess.run(["git", "init", path], capture_output=True, text=True, timeout=10)
        if r.returncode == 0:
            return f"✅ Git repo initialiseret: {path}\n{r.stdout}"
        return f"[FEJL] {r.stderr[:500]}"
    except Exception as e:
        return f"[FEJL] {e}"

def git_status(repo_path: str = "") -> str:
    """Show git status. Input: path (empty = current dir)"""
    path = repo_path.strip() or os.getcwd()
    try:
        r = subprocess.run(["git", "-C", path, "status", "--short"], capture_output=True, text=True, timeout=10)
        if r.stdout.strip():
            files = r.stdout.strip().split('\n')
            lines = ["Git Status:", ""]
            for f in files:
                status = f[:2].strip()
                fname = f[3:]
                icon = {"M": "📝", "A": "➕", "D": "❌", "?": "❓", "R": "🔄"}.get(status, "•")
                lines.append(f"  {icon} {status} {fname}")
            return "\n".join(lines)
        return "✅ Ingen ændringer — alt er committed."
    except Exception as e:
        return f"[FEJL] {e}"

def git_diff(repo_path: str = "") -> str:
    """Show git diff of changes. Input: path (empty = current dir)"""
    path = repo_path.strip() or os.getcwd()
    try:
        r = subprocess.run(["git", "-C", path, "diff", "--stat"], capture_output=True, text=True, timeout=15)
        if not r.stdout.strip():
            return "Ingen ændringer at vise (alting committed eller ingen ændringer)."
        return f"Git Diff:\n{r.stdout[:3000]}"
    except Exception as e:
        return f"[FEJL] {e}"

def git_add(repo_path: str = "") -> str:
    """Stage all changes for commit. Input: path (empty = current dir)"""
    path = repo_path.strip() or os.getcwd()
    try:
        r = subprocess.run(["git", "-C", path, "add", "-A"], capture_output=True, text=True, timeout=10)
        if r.returncode == 0:
            return "✅ Alle ændringer staged."
        return f"[FEJL] {r.stderr[:500]}"
    except Exception as e:
        return f"[FEJL] {e}"

def git_commit(message: str = "") -> str:
    """Commit staged changes. Input: commit message"""
    msg = message.strip() or f"Auto-commit {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    try:
        r = subprocess.run(["git", "commit", "-m", msg], capture_output=True, text=True, timeout=15,
                          env={**os.environ, "GIT_EDITOR": "true"})
        if r.returncode == 0:
            lines = r.stdout.strip().split('\n')
            return f"✅ Committed: {msg}\n{chr(10).join(lines[:5])}"
        # Nothing to commit?
        if "nothing to commit" in r.stdout:
            return "ℹ️ Intet at commit — ingen ændringer."
        return f"[FEJL] {r.stderr[:500]}"
    except Exception as e:
        return f"[FEJL] {e}"

def git_log(repo_path: str = "") -> str:
    """Show recent git log. Input: path (empty = current dir)"""
    path = repo_path.strip() or os.getcwd()
    try:
        r = subprocess.run(["git", "-C", path, "log", "--oneline", "-15"], 
                          capture_output=True, text=True, timeout=10)
        if r.returncode == 0 and r.stdout.strip():
            lines = ["Git Log (sidste 15 commits):", ""]
            for line in r.stdout.strip().split('\n'):
                lines.append(f"  {line}")
            return "\n".join(lines)
        return "Ingen commits endnu."
    except Exception as e:
        return f"[FEJL] {e}"

def git_push(repo_path: str = "") -> str:
    """Push to remote. Input: path (empty = current dir)"""
    path = repo_path.strip() or os.getcwd()
    try:
        r = subprocess.run(["git", "-C", path, "push"], capture_output=True, text=True, timeout=30)
        if r.returncode == 0:
            return f"✅ Push gennemført.\n{r.stdout[:500]}"
        return f"[FEJL] {r.stderr[:500]}"
    except Exception as e:
        return f"[FEJL] {e}"

def git_pull(repo_path: str = "") -> str:
    """Pull from remote. Input: path (empty = current dir)"""
    path = repo_path.strip() or os.getcwd()
    try:
        r = subprocess.run(["git", "-C", path, "pull"], capture_output=True, text=True, timeout=30)
        if r.returncode == 0:
            return f"✅ Pull gennemført.\n{r.stdout[:500]}"
        return f"[FEJL] {r.stderr[:500]}"
    except Exception as e:
        return f"[FEJL] {e}"

def git_branch(repo_path: str = "") -> str:
    """List git branches. Input: path (empty = current dir)"""
    path = repo_path.strip() or os.getcwd()
    try:
        r = subprocess.run(["git", "-C", path, "branch", "-a"], capture_output=True, text=True, timeout=10)
        if r.returncode == 0:
            return f"Branches:\n{r.stdout}"
        return f"[FEJL] {r.stderr[:500]}"
    except Exception as e:
        return f"[FEJL] {e}"