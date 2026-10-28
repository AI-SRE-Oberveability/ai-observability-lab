# Lab coordination, planning and evidence

Verified public repository: `javedkumail/ai-observability-lab`; initial source publication tracked in the lab evidence.

Read [POC_PLAN.md](POC_PLAN.md), [HLD.md](HLD.md), [POC_TRACKER.md](POC_TRACKER.md), [REMAINING.md](REMAINING.md) and [TRACKER_GUIDE.md](TRACKER_GUIDE.md). The plan is approved; this first publication is a development baseline.

`tracking/` owns the task model, state, generated status and audit history. `evidence/` holds sanitized validation reports. `scripts/` owns coordination/tracking helpers; `tests/` tests the tracker itself. `docs/` contains architecture context and proposed decisions. The lab never duplicates Terraform, workload or shared telemetry definitions owned by sibling repositories.

The local coordinator expects sibling clones under one parent directory. `compose.yaml` demonstrates that relative layout; the later release manifest will pin each repository to tested commits/releases. These are separate repositories, not submodules or a Git repository containing nested repositories.
