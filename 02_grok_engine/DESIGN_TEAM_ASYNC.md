# Async TeamEngine Refactor — Design Document

**Scope:** Refactor `core/team_engine.py` so the 6 specialist roles execute in parallel using Cline native `/team` tools, with converged outcomes and a local `GrokAgent` fallback.

**Constraint:** Architecture only — no implementation code.

---

## 1. Goals

- Replace the current sequential `run_mission()` with an async orchestration that:
  - spawns all 6 specialists concurrently,
  - dispatches their tasks in parallel via `team_run_task(..., runMode="async")`,
  - gathers results via `team_await_runs`,
  - feeds raw outputs into verifier and reporter,
  - creates/finalizes a Cline outcome with attached fragments.
- Keep a transparent fallback to a local `GrokAgent` whenever a native `/team` call fails.
- Keep `grok.py` and `grok_team.py` callers simple (sync CLI code calls `asyncio.run(...)`).

---

## 2. Role & Team Model (preserved)

The existing definitions remain unchanged:

- `ROLE_PROMPTS`: `commander`, `security`, `code`, `recon`, `verifier`, `reporter`.
- `DEFAULT_TEAMS`: maps `security_audit`, `bugbounty`, `code_refactor`, `code_audit`, `research`, `generic` to role lists.
- `_detect_team_type()` stays as the mission classifier.

No behavioral changes to prompts or team selection logic.

---

## 3. Async Lifecycle

```
mission request
│
├─▶ detect team type & roles
│
├─▶ team_create_outcome(title, required_sections)
│
├─▶ Phase A: spawn specialists concurrently
│   ├─ team_spawn_teammate(agentId, rolePrompt)
│   └─ failed roles marked as local:{role}
│
├─▶ Phase B: commander plan
│   ├─ prefer async call to commander teammate
│   └─ fallback to local LLM
│   └─ outcome_attach(plan_fragment)
│
├─▶ Phase C: dispatch specialist tasks in parallel
│   ├─ per role: team_run_task(role_agent, task, runMode="async") -> run_id
│   └─ local roles skipped; queued as local GrokAgent jobs
│
├─▶ Phase D: gather results
│   ├─ team_await_runs(run_ids) -> native results
│   ├─ failed/empty native runs fall back to local GrokAgent
│   └─ outcome_attach(specialist_output fragments)
│
├─▶ Phase E: verification
│   ├─ build verifier prompt from raw results
│   ├─ async dispatch to verifier (native or local fallback)
│   └─ outcome_attach(verification_fragment)
│
├─▶ Phase F: final report
│   ├─ build reporter prompt from results + verification
│   ├─ async dispatch to reporter (native or local fallback)
│   └─ outcome_attach(final_report_fragment)
│
└─▶ team_finalize_outcome(outcome_id)
    return formatted final report
```

---

## 4. Key Function Signatures

```python
class TeamEngine:
    def __init__(self, base_agent: Optional[GrokAgent] = None, model: Optional[str] = None) -> None: ...

    # ── public async entry point ──
    async def run_mission(
        self,
        mission: str,
        team_type: str = "auto",
        timeout: Optional[float] = None,
    ) -> str: ...

    # ── setup ──
    async def _spawn_roles(self, roles: List[str]) -> Dict[str, str]: ...
    async def _spawn_role(self, role: str) -> Tuple[str, str]: ...       # returns (role, agent_id_or_local)

    # ── planning ──
    async def _commander_plan(self, mission: str, roles: List[str]) -> str: ...

    # ── parallel dispatch & gather ──
    async def _dispatch_role_tasks(
        self,
        mission: str,
        plan: str,
        roles: List[str],
    ) -> Dict[str, str]: ...                                           # role -> run_id

    async def _gather_results(
        self,
        role_run_ids: Dict[str, str],
        timeout: Optional[float] = None,
    ) -> Dict[str, str]: ...                                           # role -> output

    async def _run_role(
        self,
        role: str,
        task_prompt: str,
        timeout: Optional[float] = None,
    ) -> str: ...                                                      # dispatch + await + fallback

    # ── convergence ──
    async def _verify(self, mission: str, results: Dict[str, str]) -> str: ...
    async def _report(
        self,
        mission: str,
        results: Dict[str, str],
        verification: str,
    ) -> str: ...

    # ── local fallback ──
    async def _local_llm(self, prompt: str, label: str = "local") -> str: ...

    # ── outcomes API ──
    async def _outcome_create(
        self,
        title: str,
        required_sections: List[str],
    ) -> Optional[str]: ...                                            # returns outcome_id

    async def _outcome_attach(
        self,
        outcome_id: str,
        section: str,
        content: str,
        source_run_id: Optional[str] = None,
    ) -> None: ...

    async def _outcome_finalize(self, outcome_id: str) -> None: ...

    # ── diagnostics (sync, small) ──
    def status(self) -> str: ...
    def _log(self, event: str, data: Dict[str, Any]) -> None: ...
```


---

## 5. Data Flow & State

### State kept inside `TeamEngine`

| Field | Type | Purpose |
|-------|------|---------|
| `self.teammates` | `Dict[str, str]` | role -> native `agentId` OR `"local:{role}"` |
| `self.outcome_id` | `Optional[str]` | active Cline outcome id |
| `self.mission_log` | `List[Dict]` | timestamped lifecycle events |
| `self.run_map` | `Dict[str, str]` | role -> async run id for Phase D |
| `self.fragments` | `Dict[str, str]` | section -> fragment id (optional cache) |

### Flow of a single mission

1. **Team selection** — `_detect_team_type()` resolves `team_type="auto"` to a concrete role list.
2. **Outcome creation** — `_outcome_create()` initializes an outcome with sections: `current_state`, `boundary_analysis`, `plan`, `specialist_outputs`, `verification`, `final_report`.
3. **Spawn** — `_spawn_roles()` runs `_spawn_role()` for every role concurrently via `asyncio.gather(..., return_exceptions=True)`. Failures are logged and the role is recorded as `local:{role}`.
4. **Plan** — `_commander_plan()` sends the plan request to the commander agent (native sync call wrapped in a thread) or falls back to `_local_llm()`. The plan is attached to the outcome under `plan`.
5. **Task construction** — the existing `_parse_plan_into_tasks()` builds per-role prompts from the plan and mission.
6. **Dispatch** — `_dispatch_role_tasks()` calls `team_run_task(..., runMode="async")` for every non-local role in parallel. Local roles are instead queued for `_local_llm()`.
7. **Gather** — `_gather_results()` passes all native run ids to `team_await_runs()`. Each returned value is mapped back to its role. Empty/failed results trigger `_local_llm()` as a retry. All successful specialist outputs are attached as fragments under `specialist_outputs`.
8. **Verify** — `_verify()` builds the verifier prompt and calls `_run_role("verifier", ...)`. Result attached to `verification`.
9. **Report** — `_report()` builds the reporter prompt and calls `_run_role("reporter", ...)`. Result attached to `final_report`.
10. **Finalize** — `_outcome_finalize()` closes the outcome.
11. **Return** — a formatted banner plus the final report string is returned to the caller.

---

## 6. Concurrency & Threading Model

- All orchestration runs on a single `asyncio` event loop inside `TeamEngine.run_mission()`.
- Cline native tools (`team_spawn_teammate`, `team_run_task`, `team_await_runs`, outcomes APIs) are synchronous wrappers injected at runtime. They are invoked via `asyncio.to_thread()` or `loop.run_in_executor()` so they never block the event loop.
- `asyncio.gather(..., return_exceptions=True)` is used for both spawn and dispatch phases so one failing role does not abort the others.
- A single timeout is supported by wrapping `team_await_runs()` in `asyncio.wait_for()`.
- Local `GrokAgent` calls are also wrapped in `asyncio.to_thread()` because `GrokAgent.run()` is synchronous.

---

## 7. Fallback Rules

| Failure point | Behavior |
|---------------|----------|
| `team_spawn_teammate` raises exception | Record role as `local:{role}`, log warning, continue mission. |
| `team_run_task` dispatch fails | Immediately route that role to `_local_llm()`. |
| `team_await_runs` returns empty/error for a role | Retry once via `_local_llm()`; log the native error. |
| Commander plan fails | Fall back to `_local_llm()` with the plan prompt. |
| Verifier/Reporter native call fails | Fall back to `_local_llm()`. |
| Outcomes API unavailable | Mission continues; outcome operations are best-effort and logged, not fatal. |

The public `run_mission()` always returns a string: either the converged report, or — in a worst-case total failure — an error summary plus the commander plan and any partial outputs.

---

## 8. Outcomes Schema

Each mission creates one Cline outcome.

**Title:** `Grok Team Mission — <team_type> — <mission_summary>`

**Required sections:**

- `current_state` — short context: mission text, detected team type, roles, timestamp.
- `boundary_analysis` — scope boundaries inferred by the commander.
- `plan` — commander tactical plan.
- `specialist_outputs` — one fragment per specialist (security, code, recon, etc.).
- `verification` — verifier findings with confidence labels.
- `final_report` — reporter markdown synthesis.

Each fragment includes the role's raw output (truncated only if necessary) and, where applicable, the `source_run_id` from `team_run_task`/`team_await_runs` for traceability.

---

## 9. Caller Integration

### `grok_team.py`

- `TeamEngine` is instantiated as today: `TeamEngine(base_agent=agent, model=agent.router.active_model)`.
- All calls to `engine.run_mission(...)` become `asyncio.run(engine.run_mission(...))`.
- A small helper can be added:

  ```python
  def _run_team_mission(agent, mission, team_type="auto") -> str:
      engine = TeamEngine(base_agent=agent, model=agent.router.active_model)
      return asyncio.run(engine.run_mission(mission, team_type=team_type))
  ```

- Interactive `/team <mission>` handler and the `--team` batch path both route through this helper.
- Session saving remains synchronous and happens after the async mission completes.

### `grok.py`

- In `handle_command()`, the `/team` branch is updated similarly:

  ```python
  if cmd.startswith("/team"):
      ...
      engine = TeamEngine(base_agent=agent, model=agent.router.active_model)
      print(asyncio.run(engine.run_mission(mission, team_type=team_type)))
      return True
  ```

- Optional: support a `--team` batch flag by delegating to the same `asyncio.run()` call before the normal `--batch` path.
- Because `grok.py` is currently synchronous, `asyncio.run()` is the cleanest integration point. If `grok.py` is later converted to async, replace `asyncio.run(...)` with `await engine.run_mission(...)`.

### Common concerns

- `asyncio.run()` must not be called inside an already-running event loop. Since both entry points are sync today, this is safe.
- History, session saving, and signal handling remain unchanged; they run outside the mission coroutine.

---

## 10. Non-Goals / Out of Scope

- Replacing `GrokAgent` with an async implementation.
- Rewriting `grok.py` or `grok_team.py` as fully async programs.
- Adding persistent team state across process restarts.
- Automatic retry/back-off beyond one local fallback per failed native call.

---

## 11. Success Criteria

- `/team audit repo for sårbarheder` spawns all 6 roles, dispatches them in parallel, awaits results, and produces a single converged report.
- A failed `team_spawn_teammate` call still completes the mission using local `GrokAgent` for that role.
- Every completed mission creates and finalizes a Cline outcome with fragments for plan, specialist outputs, verification, and final report.
- `grok.py` and `grok_team.py` continue to work as interactive / batch CLIs with no visible regression.
