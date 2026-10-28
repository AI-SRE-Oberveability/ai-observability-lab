# Lab coordination, planning and evidence

Verified public repository: `AI-SRE-Oberveability/ai-observability-lab`; reviewed source published; see evidence/publication-receipts.json.

Read [POC_PLAN.md](POC_PLAN.md), [HLD.md](HLD.md), [POC_TRACKER.md](POC_TRACKER.md), [REMAINING.md](REMAINING.md) and [TRACKER_GUIDE.md](TRACKER_GUIDE.md). The plan is approved and all four reviewed source baselines are published. See HLD.md and POC_TRACKER.md for the next local validation tasks.

`tracking/` owns the task model, state, generated status and audit history. `evidence/` holds sanitized validation reports. `scripts/` owns coordination/tracking helpers; `tests/` tests the tracker itself. `docs/` contains architecture context and proposed decisions. The lab never duplicates Terraform, workload or shared telemetry definitions owned by sibling repositories.

[Shared GitHub Project](https://github.com/orgs/AI-SRE-Oberveability/projects/1): 36 task issues across all four repositories, with Delivery board and All tasks views. The Project is private to authorized organization members; repository source remains public. After each recorded work step, run `python scripts/sync_github_project.py --apply` to mirror evidence status and managed issue content. See TRACKER_GUIDE.md for authentication and recovery.

The local coordinator expects sibling clones under one parent directory. `compose.yaml` demonstrates that relative layout; the later release manifest will pin each repository to tested commits/releases. These are separate repositories, not submodules or a Git repository containing nested repositories.
