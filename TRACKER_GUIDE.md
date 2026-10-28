# Tracker operating guide

The user selected updates **after each work step**. There is no scheduled job, external service, account connection or deployment permission in this tracker. It uses Python's standard library.

`tracking/plan.json` defines 36 tasks, owners, dependencies, gates, source/artifact paths and acceptance criteria. `tracking/state.json` stores current outcomes and user decisions. `tracking/events.jsonl` retains the update history. Refresh generates `POC_TRACKER.md`, `REMAINING.md` and `tracking/status.json`.

From the `personal-ai-observability` parent workspace:

```powershell
python ai-observability-lab/scripts/poc_tracker.py refresh
python -m unittest discover -s ai-observability-lab/tests -v
```

After doing one authorized work step, save sanitized evidence under `ai-observability-lab/evidence` and run:

```powershell
python ai-observability-lab/scripts/poc_tracker.py record P1.1 --status done --note "Draft review completed; findings recorded" --evidence ai-observability-lab/evidence/draft-review.md
```

This is an example for future accepted work; it is not run while G0 is pending. `record` always refreshes the views. Use `draft`, `in_progress`, `blocked` or `failed` for incomplete work. `done` needs evidence, required artifacts, completed dependencies and accepted applicable gates. A later changed source/evidence file causes `needs_revalidation` on refresh. Watch lists must be maintained as new files become relevant; a hash proves consistency only for the watched files, not semantic correctness or external cloud state.

Each recorded step updates the latest-work summary. When the architecture changes, update `HLD.md` and use `record --hld-current "Updated current design"`; the generated tracker then displays that current summary alongside next/remaining work. Confirmed user choices are retained in `tracking/state.json` independently of pending implementation gates.

Record a decision only after the user actually supplies applicable authorization:

```powershell
python ai-observability-lab/scripts/poc_tracker.py decide G0 --status accepted --note "Reference the user's actual acceptance message here"
```

The script records decisions; it does not obtain consent or authorize account access. No decision is accepted in the initial state. Pending gates are not automatic permission questions: ask only when the next accepted step depends on them, and preserve existing scoped authorization.

Status meanings:

- `draft`: some expected files exist; delivery has not been accepted.
- `planned`: pending work with no recorded outcome.
- `done`: the recorded work-step acceptance has evidence, matching source/evidence hashes and satisfied dependencies/gates.
- `needs_revalidation`: evidence disappeared/changed, watched sources changed, or a required artifact is missing.
- `waiting_for_decision` / `blocked`: a decision or dependency prevents acceptance.
- `failed`: an observed unsuccessful check remains visible.
- `deferred`: an explicit deferral, with reason; it does not count as completed or satisfy dependent work.

The tracker never starts applications, reruns their tests, contacts Azure/GitHub/Dynatrace or changes infrastructure. Engineering steps and their actual checks remain separately authorized work. There is no claim that the tracker can independently verify external environments from local file presence.

Every progress update follows the HLD rhythm: current design, change, next step, remaining work. Update HLD.md when the architecture changes, then refresh the tracker. Read the generated remaining-work list before selecting the next task.

## Shared GitHub Project synchronization

The shared Project is owned by `AI-SRE-Oberveability`. `tracking/github-project.json` pins its existing ID/number and maps task IDs to managed issues and Project items across the four repositories. Setup reuses the existing Project; it never creates a duplicate or changes its visibility.

After each work step, record the actual local result, refresh the tracker, then synchronize:

```powershell
python ai-observability-lab/scripts/sync_github_project.py
python ai-observability-lab/scripts/sync_github_project.py --apply
```

The default is a local dry-run. `--apply` is the explicit network mutation step and updates only the approved organization's four repositories and mapped Project. It preserves human notes outside managed issue-body blocks. Done is assigned only to locally accepted `done` tasks; drafts, blocked work and pending decisions keep their exact value in Evidence status. The board's three normal columns summarize Todo, In Progress and Done. Dependencies and acceptance/evidence remain visible on each issue and in Project fields.

Use GitHub CLI signed in as the approved personal administrator with `project` scope. The user explicitly approved that additional scope. On a fresh machine, use the supported secure `gh auth login --scopes project` flow and decline Git helper reconfiguration if offered. Existing GitLab credentials/global helpers must remain unchanged. The script captures the token privately from CLI authentication; it never stores tokens in repository files or logs. It supports a normal CLI installation or the ignored portable runtime used for this setup.

New task IDs are created idempotently using stable managed markers; existing unrelated issues are preserved. A run stops on owner, identity, duplicate-task or API verification errors instead of claiming a successful sync. Project and issue pagination is intentionally bounded for this small lab; extend it before exceeding the documented 100-item/page limits.
