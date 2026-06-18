#!/usr/bin/env python3
"""
TEAM ENGINE v99.9 — production async multi-agent orchestrator
"""

import os
import sys
import time
import asyncio
import traceback
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

_TEAM_DIR = os.path.dirname(os.path.abspath(__file__))
_GROK_DIR = os.path.dirname(_TEAM_DIR)
sys.path.insert(0, _GROK_DIR)
sys.path.insert(0, _TEAM_DIR)

from core.agent import GrokAgent, Colors

try:
    from core.config import DEFAULT_MODEL
except ImportError:
    from config import DEFAULT_MODEL


class TeamEngine:
    ROLE_PROMPTS: Dict[str, str] = {
        "commander": """You are COMMANDER — the mission conductor.
Your job: read the user's request, break it into sub-tasks, assign them to the right specialists, and synthesize their outputs into ONE coherent final answer.
You NEVER do the work yourself; you delegate and verify.""",
        "security": """You are SECURITY EXPERT — offensive security, bug bounty, vulnerability analysis, exploit verification.
Tools you love: bash, subfinder, httpx, nmap, ffuf, nuclei, corsy, exploit_verify, cve_lookup.
Output format: findings with Severity / Evidence / FP check / Reproducer.""",
        "code": """You are CODE EXPERT — Python architect, refac, debug, audit, test writer.
You use: bash, file_read, file_write, search_codebase, git_*, python tools.
Write complete, working code. No placeholders.""",
        "recon": """You are RECON EXPERT — OSINT, asset discovery, fingerprinting, scope mapping.
Tools: subfinder, httpx, dig, nmap, whois, web_search, curl_api.""",
        "verifier": """You are VERIFIER — skeptical fact-checker and false-positive hunter.
Challenge claims. Demand evidence, exact commands, reproducibility.
Output: "Verified / Needs manual / Filtered out" with reasoning.""",
        "reporter": """You are REPORTER — markdown formatter and final findings writer.
Turn raw output into clean, structured, actionable reports.""",
    }

    DEFAULT_TEAMS: Dict[str, List[str]] = {
        "security_audit": ["commander", "security", "recon", "verifier", "reporter"],
        "bugbounty":      ["commander", "security", "recon", "verifier", "reporter"],
        "code_refactor":  ["commander", "code", "verifier", "reporter"],
        "code_audit":     ["commander", "code", "security", "verifier", "reporter"],
        "research":       ["commander", "recon", "security", "reporter"],
        "generic":        ["commander", "security", "code", "recon", "verifier", "reporter"],
    }

    OUTCOME_SECTIONS = [
        "current_state",
        "boundary_analysis",
        "plan",
        "specialist_outputs",
        "verification",
        "final_report",
    ]

    def __init__(self, base_agent: GrokAgent = None, model: str = None):
        self.base_agent = base_agent
        self.model = model or DEFAULT_MODEL
        self.teammates: Dict[str, str] = {}
        self.mission_log: List[Dict[str, Any]] = []
        self.outcomes: Dict[str, Any] = {}
        self.start_time: Optional[float] = None
        self.active = False
        self.colors = Colors()
        self.outcome_id: Optional[str] = None
        self.run_map: Dict[str, str] = {}
        self.fragments: Dict[str, str] = {}
        self._native_available: Optional[bool] = None

    def run_mission(self, mission: str, team_type: str = "auto", timeout: Optional[float] = None) -> str:
        try:
            return asyncio.run(self.async_run_mission(mission, team_type=team_type, timeout=timeout))
        except Exception as e:
            tb = traceback.format_exc()
            self._log("mission_fatal", {"error": str(e), "traceback": tb})
            return f"TEAM MISSION ERROR: {e}\n{tb[:2000]}"

    async def async_run_mission(self, mission: str, team_type: str = "auto", timeout: Optional[float] = None) -> str:
        """Async orchestration: spawn → plan → dispatch → gather → verify → report → converge.

        NOTE: TeamEngine is cloud-only. Local Ollama fallback is intentionally disabled.
        We force OLLAMA_CLOUD=1 so every sub-agent call routes through Ollama Cloud.
        """
        # Force cloud mode for the entire process if not explicitly disabled.
        if os.getenv("OLLAMA_CLOUD", "") != "0":
            os.environ["OLLAMA_CLOUD"] = "1"

        self.start_time = time.time()
        self.active = True
        self._log("mission_start", {"mission": mission, "team_type": team_type})

        if team_type == "auto":
            team_type = self._detect_team_type(mission)
        roles = list(self.DEFAULT_TEAMS.get(team_type, self.DEFAULT_TEAMS["generic"]))
        for r in ("security", "code", "recon", "verifier", "reporter", "commander"):
            if r not in roles:
                roles.append(r)

        self._print_banner(mission, roles)

        self.outcome_id = await self._outcome_create(
            title=f"Grok Team Mission — {team_type} — {mission[:60]}",
            required_sections=self.OUTCOME_SECTIONS,
        )
        await self._outcome_attach("current_state", self._current_state_fragment(mission, team_type, roles))

        await self._spawn_roles(roles)
        await self._outcome_attach("boundary_analysis", self._boundary_analysis_fragment(mission, roles))

        plan = await self._commander_plan(mission, roles)
        await self._outcome_attach("plan", f"## Commander Plan\n\n{plan}\n")
        print(f"{self.colors.YELLOW}COMMANDER PLAN:{self.colors.END}\n{plan}\n")

        tasks = self._parse_plan_into_tasks(plan, mission, roles)
        worker_roles = [r for r in roles if r != "commander" and r in tasks]
        print(f"{self.colors.CYAN}Dispatching {len(worker_roles)} specialists in parallel...{self.colors.END}\n")
        self.run_map = await self._dispatch_role_tasks(worker_roles, tasks)

        results: Dict[str, str] = await self._gather_results(self.run_map, timeout=timeout)
        for role, output in results.items():
            await self._outcome_attach("specialist_outputs", f"### {role.upper()}\n\n{output[:4000]}\n", source_run_id=self.run_map.get(role))

        verification = await self._verify(mission, results)
        await self._outcome_attach("verification", f"## Verifier\n\n{verification[:6000]}\n")

        final_report = await self._report(mission, results, verification)
        await self._outcome_attach("final_report", f"## Final Report\n\n{final_report[:8000]}\n")

        await self._outcome_finalize()

        elapsed = time.time() - self.start_time
        self._log("mission_complete", {"elapsed_sec": elapsed, "roles": roles})
        self.active = False
        return f"TEAM MISSION COMPLETE — {elapsed:.1f}s\n\n{final_report}"

    def _print_banner(self, mission: str, roles: List[str]):
        print(f"\nGROK TEAM — SWARM DEPLOYMENT")
        print(f"Mission: {mission[:60]}")
        print(f"Team:    {', '.join(roles)}\n")

    async def _spawn_roles(self, roles: List[str]):
        results = await asyncio.gather(*(self._spawn_role(role) for role in roles), return_exceptions=True)
        for role, res in zip(roles, results):
            if isinstance(res, Exception):
                agent_id = f"local:{role}"
                self.teammates[role] = agent_id
                print(f"! {role} fallback to local agent ({res})")
                self._log("spawn_fallback", {"role": role, "error": str(res)})
            else:
                self.teammates[role] = res
                print(f"✓ Spawned {role} -> {res}")

    async def _spawn_role(self, role: str) -> str:
        """Spawn a teammate. Native Cline tools preferred, but fall back to a local GrokAgent handle."""
        agent_id = f"local:{role}_{int(time.time() * 1000) % 100000}"
        if self._native_tools_available():
            try:
                prompt = self.ROLE_PROMPTS.get(role, self.ROLE_PROMPTS["commander"])
                def _spawn():
                    from functions import team_spawn_teammate
                    team_spawn_teammate(agentId=agent_id, rolePrompt=prompt)
                    return agent_id
                return await asyncio.to_thread(_spawn)
            except Exception as e:
                self._log("spawn_native_error", {"role": role, "error": str(e)})
        return agent_id

    async def _commander_plan(self, mission: str, roles: List[str]) -> str:
        prompt = f"You are COMMANDER. Mission: {mission}\nAvailable specialists: {', '.join(roles)}\nCreate a concise tactical plan (max 12 bullets) specifying what each specialist should do."
        return await self._run_role("commander", prompt)

    async def _dispatch_role_tasks(self, roles: List[str], tasks: Dict[str, str]) -> Dict[str, str]:
        run_map: Dict[str, str] = {}
        async def _dispatch(role: str) -> Tuple[str, Optional[str]]:
            task = tasks.get(role, "")
            agent_id = self.teammates.get(role)
            if not agent_id or agent_id.startswith("local:"):
                return role, None
            try:
                def _dispatch_native():
                    from functions import team_run_task
                    return team_run_task(agentId=agent_id, task=task, runMode="async")
                run = await asyncio.to_thread(_dispatch_native)
                run_id = run.get("runId") if isinstance(run, dict) else None
                if not run_id:
                    return role, None
                print(f"-> {role} queued (runId={run_id})")
                return role, run_id
            except Exception as e:
                print(f"[dispatch fallback] {role}: {e}")
                self._log("dispatch_fallback", {"role": role, "error": str(e)})
                return role, None
        results = await asyncio.gather(*(_dispatch(role) for role in roles))
        for role, run_id in results:
            if run_id:
                run_map[role] = run_id
        self.run_map = run_map
        return run_map

    async def _gather_results(self, run_map: Dict[str, str], timeout: Optional[float] = None) -> Dict[str, str]:
        results: Dict[str, str] = {}
        native_run_ids = list(run_map.values())
        native_results: Dict[str, Any] = {}

        if native_run_ids and self._native_tools_available():
            try:
                def _await():
                    from functions import team_await_runs
                    return team_await_runs()
                if timeout:
                    awaited = await asyncio.wait_for(asyncio.to_thread(_await), timeout=timeout)
                else:
                    awaited = await asyncio.to_thread(_await)
                for role, run_id in run_map.items():
                    entry = awaited.get(run_id) if isinstance(awaited, dict) else None
                    if isinstance(entry, dict):
                        native_results[role] = entry.get("result") or entry.get("output") or ""
                    elif isinstance(entry, str):
                        native_results[role] = entry
            except Exception as e:
                self._log("await_error", {"error": str(e)})
                print(f"[await_runs failed, using local fallback for all native runs]")

        for role in self.run_map.keys():
            output = native_results.get(role, "")
            if not output or not str(output).strip():
                task = self._role_task_for(role)
                print(f"\n{role.upper()} executing locally...")
                output = await self._local_llm(task, label=role)
            else:
                print(f"\n{role.upper()} completed (native)")
            results[role] = str(output)

        for role, agent_id in self.teammates.items():
            if role == "commander" or role in results:
                continue
            if agent_id.startswith("local:"):
                task = self._role_task_for(role)
                print(f"\n{role.upper()} executing locally...")
                results[role] = await self._local_llm(task, label=role)

        return results

    def _role_task_for(self, role: str) -> str:
        return f"You are {role.upper()} EXPERT. Execute your specialist responsibilities for this mission and return concise, evidence-backed output."

    async def _verify(self, mission: str, results: Dict[str, str]) -> str:
        parts = [f"### {role.upper()} OUTPUT\n{output[:3000]}\n" for role, output in results.items()]
        prompt = f"You are VERIFIER. Mission: {mission}\n\nReview the following teammate outputs. Mark each claim: Verified / Needs manual / Filtered out.\n\n" + "\n".join(parts)
        return await self._run_role("verifier", prompt)

    async def _report(self, mission: str, results: Dict[str, str], verification: str) -> str:
        parts = [f"### {role.upper()}\n{output[:2500]}\n" for role, output in results.items()]
        parts.append(f"### VERIFIER\n{verification[:2000]}\n")
        prompt = f"You are REPORTER. Mission: {mission}\n\nSynthesize teammate outputs + verifier notes into ONE clean, actionable final report.\n\n" + "\n".join(parts)
        return await self._run_role("reporter", prompt)

    async def _run_role(self, role: str, task: str) -> str:
        agent_id = self.teammates.get(role)
        if agent_id and not agent_id.startswith("local:"):
            try:
                def _sync_run():
                    from functions import team_run_task
                    run = team_run_task(agentId=agent_id, task=task, runMode="sync")
                    if isinstance(run, dict):
                        return run.get("result") or run.get("output") or ""
                    return str(run)
                result = await asyncio.to_thread(_sync_run)
                if result and str(result).strip():
                    return str(result)
            except Exception as e:
                self._log("role_native_error", {"role": role, "error": str(e)})
                print(f"[{role} native failed, using local fallback]")
        return await self._local_llm(task, label=role)

    async def _local_llm(self, prompt: str, label: str = "local") -> str:
        """Cloud-only fallback: force OLLAMA_CLOUD=1 then run via GrokAgent."""
        try:
            # User policy: never local models. Always route through Ollama Cloud.
            if os.getenv("OLLAMA_CLOUD", "") != "0":
                os.environ["OLLAMA_CLOUD"] = "1"

            def _run():
                local = GrokAgent(model=self.model, provider="ollama")
                local.interactive = False
                return local.run(prompt, stream=False) or "[no output]"
            return await asyncio.to_thread(_run)
        except Exception as e:
            self._log("local_llm_error", {"label": label, "error": str(e)})
            return f"[{label} LLM error: {e}]"

    async def _outcome_create(self, title: str, required_sections: List[str]) -> Optional[str]:
        try:
            def _create():
                from functions import team_create_outcome
                outcome = team_create_outcome(title=title, requiredSections=required_sections)
                return outcome.get("outcomeId") if isinstance(outcome, dict) else None
            outcome_id = await asyncio.to_thread(_create)
            if outcome_id:
                self.outcome_id = outcome_id
                self._log("outcome_created", {"outcome_id": outcome_id})
            return outcome_id
        except Exception as e:
            self._log("outcome_create_error", {"error": str(e)})
            return None

    async def _outcome_attach(self, section: str, content: str, source_run_id: Optional[str] = None) -> None:
        if not self.outcome_id:
            return
        try:
            kw = {"outcomeId": self.outcome_id, "section": section, "content": content}
            if source_run_id:
                kw["sourceRunId"] = source_run_id
            def _attach():
                from functions import team_attach_outcome_fragment
                return team_attach_outcome_fragment(**kw)
            fragment = await asyncio.to_thread(_attach)
            if isinstance(fragment, dict) and "fragmentId" in fragment:
                self.fragments[section] = fragment["fragmentId"]
        except Exception as e:
            self._log("outcome_attach_error", {"section": section, "error": str(e)})

    async def _outcome_finalize(self) -> None:
        if not self.outcome_id:
            return
        try:
            def _finalize():
                from functions import team_finalize_outcome
                return team_finalize_outcome(outcomeId=self.outcome_id)
            await asyncio.to_thread(_finalize)
            self._log("outcome_finalized", {"outcome_id": self.outcome_id})
        except Exception as e:
            self._log("outcome_finalize_error", {"error": str(e)})

    def _native_tools_available(self) -> bool:
        if self._native_available is not None:
            return self._native_available
        try:
            from functions import team_run_task  # noqa: F401
            self._native_available = True
        except Exception:
            self._native_available = False
        return self._native_available

    def _parse_plan_into_tasks(self, plan: str, mission: str, roles: List[str]) -> Dict[str, str]:
        tasks: Dict[str, str] = {}
        for role in roles:
            if role == "commander":
                continue
            tasks[role] = (
                f"You are {role.upper()} EXPERT.\n"
                f"Mission: {mission}\n"
                f"Commander plan:\n{plan}\n\n"
                f"Your task: Execute ONLY the parts assigned to you as {role}. "
                f"Return concise, evidence-backed output."
            )
        return tasks

    def _current_state_fragment(self, mission: str, team_type: str, roles: List[str]) -> str:
        return f"**Mission:** {mission}\n\n**Team type:** `{team_type}`\n\n**Roles:** {', '.join(roles)}\n\n**Started:** {datetime.now().isoformat()}"

    def _boundary_analysis_fragment(self, mission: str, roles: List[str]) -> str:
        return f"- Mission: {mission}\n- Specialists: {', '.join(roles)}\n- Mode: async parallel; native Cline /team tools if available, otherwise local GrokAgent fallbacks via Ollama Cloud."

    def _detect_team_type(self, mission: str) -> str:
        m = mission.lower()
        if any(w in m for w in ["sårbarhed", "vuln", "exploit", "bug bounty", "pentest", "audit security"]):
            return "security_audit"
        if any(w in m for w in ["refactor", "rewrite", "fix code", "python", "implement"]):
            return "code_refactor"
        if any(w in m for w in ["code audit", "review code", "security code", "audit repo"]):
            return "code_audit"
        if any(w in m for w in ["research", "find", "osint", "lookup", "discover"]):
            return "research"
        return "generic"

    def _log(self, event: str, data: Dict[str, Any]):
        self.mission_log.append({"ts": datetime.now().isoformat(), "event": event, "data": data})

    def status(self) -> str:
        lines = ["TEAM STATUS", f"active: {self.active}", f"model: {self.model}", f"outcome_id: {self.outcome_id or 'none'}", f"teammates: {len(self.teammates)}"]
        for role, agent_id in sorted(self.teammates.items()):
            lines.append(f"  • {role}: {agent_id}")
        if self.mission_log:
            lines.append(f"log events: {len(self.mission_log)}")
        return "\n".join(lines)


if __name__ == "__main__":
    print("TeamEngine loaded. Roles:", list(TeamEngine.ROLE_PROMPTS.keys()))
    engine = TeamEngine(model=DEFAULT_MODEL)
    print(engine.status())
