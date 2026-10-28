# Tracker operating guide

The user selected updates **after each work step**. There is no scheduled job, external service, account connection or deployment permission in this tracker. It uses Python's standard library.

`tracking/plan.json` defines 33 tasks, owners, dependencies, gates, source/artifact paths and acceptance criteria. `tracking/state.json` stores current outcomes and user decisions. `tracking/events.jsonl` retains the update history. Refresh generates `POC_TRACKER.md`, `REMAINING.md` and `tracking/status.json`.

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
