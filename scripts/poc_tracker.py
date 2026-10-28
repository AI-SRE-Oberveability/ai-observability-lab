"""Event-driven POC tracker; standard library only, no network or deployment actions."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
LAB = BASE / "ai-observability-lab"
TRACKING = LAB / "tracking"
EXCLUDE = {".git", ".venv", ".runtime", "__pycache__", ".pytest_cache", ".ruff_cache"}


def now():
    return datetime.now(timezone(timedelta(hours=4))).isoformat(timespec="seconds")


def write_json(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def owned_path(base, name):
    path = (base / name).resolve()
    if not path.is_relative_to(base.resolve()):
        raise ValueError("Tracker paths must stay inside the lab workspace")
    return path


def snapshot(base, names):
    """Hash explicit evidence/source paths without reading credentials or runtime caches."""
    result = {}
    for name in names:
        root = owned_path(base, name)
        paths = sorted(root.rglob("*")) if root.is_dir() else [root]
        for path in paths:
            if not path.is_file() or set(path.relative_to(base).parts) & EXCLUDE:
                continue
            if path.name.startswith(".env") or path.suffix in {
                ".key",
                ".pem",
                ".tfvars",
            }:
                continue
            if not path.resolve().is_relative_to(base.resolve()):
                raise ValueError("Source symlink leaves the workspace")
            result[path.relative_to(base).as_posix()] = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
    return result


def validate_plan(plan):
    tasks = {task["id"]: task for task in plan["tasks"]}
    if len(tasks) != len(plan["tasks"]):
        raise ValueError("Duplicate task ID")
    visited, active = set(), set()

    def visit(task_id):
        if task_id not in tasks:
            raise ValueError(f"Unknown dependency: {task_id}")
        if task_id in active:
            raise ValueError("Cyclic task dependency")
        if task_id in visited:
            return
        active.add(task_id)
        for dependency in tasks[task_id]["depends_on"]:
            visit(dependency)
        for gate in tasks[task_id]["gates"]:
            if gate not in plan["gates"]:
                raise ValueError(f"Unknown gate: {gate}")
        decision = tasks[task_id].get("decision")
        if decision and decision not in plan["gates"]:
            raise ValueError(f"Unknown decision: {decision}")
        active.remove(task_id)
        visited.add(task_id)

    for task_id in tasks:
        visit(task_id)
    return tasks


def derive(plan, state, base):
    tasks = validate_plan(plan)
    rows = {}

    def derive_task(task_id):
        if task_id in rows:
            return rows[task_id]
        task = tasks[task_id]
        dependencies = [derive_task(item) for item in task["depends_on"]]
        blocked_by = [item["id"] for item in dependencies if item["status"] != "done"]
        blocked_by += [
            gate
            for gate in task["gates"]
            if state["decisions"].get(gate, {}).get("status") != "accepted"
        ]
        record = state["steps"].get(task_id, {})
        present = [
            name for name in task["artifacts"] if owned_path(base, name).exists()
        ]
        missing = [name for name in task["artifacts"] if name not in present]
        status = record.get("status", "draft" if present else "planned")
        if status == "done":
            unchanged = snapshot(base, task["watch"]) == record.get(
                "source_hashes"
            ) and snapshot(base, record.get("evidence", [])) == record.get(
                "evidence_hashes"
            )
            if not unchanged or missing or not record.get("evidence_hashes"):
                status = "needs_revalidation"
            elif blocked_by:
                status = "blocked"
        decision = task.get("decision")
        if decision:
            accepted = state["decisions"].get(decision, {}).get("status") == "accepted"
            status = "done" if accepted and not blocked_by else "waiting_for_decision"
        rows[task_id] = {
            **task,
            "status": status,
            "blocked_by": blocked_by,
            "artifacts_present": present,
            "artifacts_missing": missing,
            "evidence": record.get("evidence", []),
            "note": record.get("note", ""),
            "ready": not blocked_by and status not in {"done", "deferred"},
        }
        return rows[task_id]

    return [derive_task(task["id"]) for task in plan["tasks"]]


def cell(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def render(plan, state, base, lab):
    rows = derive(plan, state, base)
    updated = now()
    counts = Counter(row["status"] for row in rows)
    paused = state["decisions"].get("G0", {}).get("status") != "accepted"
    execution = (
        "PAUSED — plan/HLD review pending (G0)"
        if paused
        else "Plan accepted; follow task gates"
    )
    hld = state.get("hld", {})
    remaining_phases = [
        phase
        for phase in plan["phases"]
        if any(r["id"].startswith(phase + ".") and r["status"] != "done" for r in rows)
    ]
    lines = [
        "# Automated POC tracker",
        "",
        f"Updated: {updated} (Asia/Dubai).",
        f"Execution: **{execution}**.",
        "",
        "Updates occur after each work step. This document is generated by `scripts/poc_tracker.py`.",
        "Source: `tracking/plan.json` + `tracking/state.json`; audit history: `tracking/events.jsonl`.",
        "",
        f"Completed task deliverables: **{counts['done']} / {len(rows)}**. Task counts are not an effort-weighted POC completion percentage.",
        "Draft artifacts and an earlier test run do not establish accepted end-to-end delivery.",
        "",
        "## High-level update",
        "",
        "- Current design: "
        + hld.get("current", "See HLD.md for the current validated boundaries."),
        "- Target design: " + hld.get("target", "See HLD.md for the proposed target."),
        "- Latest work step: "
        + hld.get("last_change", "Plan and tracker preparation."),
        "- Next: review plan/HLD and resolve G0."
        if paused
        else "- Next ready steps: "
        + ", ".join(row["id"] for row in rows if row["ready"]),
        "- Remaining phases: "
        + ", ".join(remaining_phases)
        + ". Full steps are in REMAINING.md.",
        "",
        "## Confirmed choices",
        "",
        *["- " + choice for choice in state.get("confirmed_choices", [])],
        "",
        "## Decisions",
        "",
        "| Gate | Status | Decision needed |",
        "| --- | --- | --- |",
    ]
    for gate, description in plan["gates"].items():
        lines.append(
            f"| {gate} | {state['decisions'].get(gate, {}).get('status', 'pending')} | {cell(description)} |"
        )
    lines += [
        "",
        "## Task summary",
        "",
        "| Phase | Done / total | Drafts | Remaining |",
        "| --- | --- | --- | --- |",
    ]
    for phase, title in plan["phases"].items():
        items = [row for row in rows if row["id"].split(".")[0] == phase]
        completed = sum(row["status"] == "done" for row in items)
        drafted = sum(row["status"] == "draft" for row in items)
        lines.append(
            f"| {phase}: {title} | {completed}/{len(items)} | {drafted} | {len(items) - completed} |"
        )
    for phase, title in plan["phases"].items():
        lines += [
            "",
            f"## {phase} — {title}",
            "",
            "| Step | Work / owner | Status | Depends on / waits for | Evidence |",
            "| --- | --- | --- | --- | --- |",
        ]
        for row in [r for r in rows if r["id"].split(".")[0] == phase]:
            waits = ", ".join(row["blocked_by"]) or (
                "Ready for review" if row["ready"] else "—"
            )
            evidence = (
                ", ".join(
                    f"[{Path(p).name}]({Path(p).relative_to(lab.name).as_posix()})"
                    for p in row["evidence"]
                )
                or "None recorded"
            )
            lines.append(
                f"| {row['id']} | {cell(row['title'])} — {cell(row['owner'])} | {row['status']} | {cell(waits)} | {evidence} |"
            )
    lines += ["", "## Known gaps", ""] + [
        f"- {gap}" for gap in state.get("known_gaps", [])
    ]
    lines += [
        "",
        "## Interpretation",
        "",
        "`done` requires recorded evidence, unchanged watched sources, satisfied dependencies and accepted applicable gates. `draft` means artifacts exist; `planned` means work is pending. `needs_revalidation` means proof/source files changed or evidence disappeared. `waiting_for_decision`, `blocked`, `failed` and `deferred` remain visible. Full acceptance criteria are in `tracking/plan.json`.",
        "",
    ]
    (lab / "POC_TRACKER.md").write_text("\n".join(lines), encoding="utf-8")
    remaining = [
        "# What remains",
        "",
        f"Updated: {updated} (Asia/Dubai).",
        "",
        f"Execution: **{execution}**.",
        "",
        "Next action: user review of POC_PLAN.md and HLD.md."
        if paused
        else "Next action: select a ready step from POC_TRACKER.md.",
        "",
    ]
    for phase, title in plan["phases"].items():
        items = [
            row
            for row in rows
            if row["id"].split(".")[0] == phase and row["status"] != "done"
        ]
        if not items:
            continue
        remaining += [f"## {phase} — {title}", ""]
        for row in items:
            remaining += [
                f"- **{row['id']} {row['title']}** ({row['status']}). Acceptance: {row['acceptance']}"
            ]
        remaining.append("")
    (lab / "REMAINING.md").write_text("\n".join(remaining), encoding="utf-8")
    write_json(
        lab / "tracking/status.json",
        {
            "updated_at": updated,
            "execution": execution,
            "counts": dict(counts),
            "tasks": rows,
        },
    )
    print(
        f"Tracker refreshed: {counts['done']}/{len(rows)} task deliverables done; {execution}"
    )
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser(
        "refresh",
        help="Inventory files, check evidence freshness, regenerate views; run no workloads",
    )
    step = sub.add_parser(
        "record", help="Record one actual work-step outcome and regenerate views"
    )
    step.add_argument("task")
    step.add_argument(
        "--status",
        required=True,
        choices=["draft", "in_progress", "blocked", "failed", "done", "deferred"],
    )
    step.add_argument("--note", required=True)
    step.add_argument(
        "--evidence",
        action="append",
        default=[],
        help="Workspace-relative file in ai-observability-lab/evidence",
    )
    step.add_argument(
        "--hld-current",
        help="Update the current-design summary if this step changed it; update HLD.md too",
    )
    decision = sub.add_parser(
        "decide", help="Record an already supplied user decision; never infer consent"
    )
    decision.add_argument("gate")
    decision.add_argument("--status", required=True, choices=["accepted", "pending"])
    decision.add_argument(
        "--note",
        required=True,
        help="Reference the user's applicable authorization or requested revision",
    )
    args = parser.parse_args()
    plan = json.loads((TRACKING / "plan.json").read_text(encoding="utf-8"))
    state = json.loads((TRACKING / "state.json").read_text(encoding="utf-8"))
    tasks = validate_plan(plan)
    if args.command == "decide":
        if args.gate not in plan["gates"]:
            parser.error("Unknown gate")
        state["decisions"][args.gate] = {
            "status": args.status,
            "note": args.note,
            "at": now(),
        }
    elif args.command == "record":
        if args.task not in tasks:
            parser.error("Unknown task")
        task = tasks[args.task]
        if task.get("decision"):
            parser.error("Use decide for user decision steps")
        for name in args.evidence:
            path = owned_path(BASE, name)
            if not path.is_relative_to(LAB / "evidence") or not path.is_file():
                parser.error(
                    "Evidence must be an existing file under ai-observability-lab/evidence"
                )
        row = next(row for row in derive(plan, state, BASE) if row["id"] == args.task)
        if args.status == "done" and (
            row["blocked_by"] or row["artifacts_missing"] or not args.evidence
        ):
            parser.error(
                "Completion needs evidence, required artifacts and satisfied dependencies/gates"
            )
        state["steps"][args.task] = {
            "status": args.status,
            "note": args.note,
            "at": now(),
            "evidence": args.evidence,
            "source_hashes": snapshot(BASE, task["watch"]),
            "evidence_hashes": snapshot(BASE, args.evidence),
        }
        state.setdefault("hld", {})["last_change"] = f"{args.task}: {args.note}"
        if args.hld_current:
            state["hld"]["current"] = args.hld_current
    if args.command != "refresh":
        event = {
            "at": now(),
            "command": args.command,
            **{key: value for key, value in vars(args).items() if key != "command"},
        }
        with (TRACKING / "events.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(event, ensure_ascii=False) + "\n")
        write_json(TRACKING / "state.json", state)
    render(plan, state, BASE, LAB)


if __name__ == "__main__":
    main()
