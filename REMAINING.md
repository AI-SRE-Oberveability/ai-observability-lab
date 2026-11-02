# What remains

Updated: 2026-11-01T16:10:15+04:00 (Asia/Dubai).

Execution: **Plan accepted; follow task gates**.

Next action: select a ready step from POC_TRACKER.md.

## P2 — Establish personal GitHub delivery

- **P2.4 Pin image digests and multi-repository release manifest** (in_progress). Acceptance: Known commits/releases and immutable images reproduce the local demo; scoped coordination credentials are documented.

## P3 — Plan and deploy personal Azure

- **P3.1 Confirm personal Azure targets, region and budget** (waiting_for_decision). Acceptance: Supplied exact tenant/subscription and personal identity are matched; region/budget/currency and model requirement recorded.
- **P3.2 Produce costed Azure HLD and runner/network design** (draft). Acceptance: Dated active/idle costs, AKS/APIM SKU and network/runner reachability, identity boundaries, retention and optional Managed footprint documented; no cloud authorization inferred.
- **P3.3 Prepare Terraform, state bootstrap and scoped OIDC** (planned). Acceptance: IaC validates with provider locks; private state ownership, scoped RBAC/federation, actual OIDC subject and resource tags are verified.
- **P3.4 Review concrete IaC plan and authorize spending scope** (waiting_for_decision). Acceptance: Concrete plan, cost assumptions, resource scope and lifecycle presented and authorized once for the agreed bounds.
- **P3.5 Deploy pinned Azure baseline through GitHub Actions** (planned). Acceptance: Only authorized resources deploy; workflow, smoke, telemetry and cloud-mock release evidence saved.
- **P3.6 Verify cloud start/stop and scoped destroy/recreate** (planned). Acceptance: Owned lifecycle works for exact scope; remaining stopped-resource costs/state and evidence retention documented.
- **P3.7 Prepare Terraform APIM governance and versioned policy contracts** (planned). Acceptance: Terraform/provider coverage, complete backend/access inventory, three identity boundaries, network/diagnostic ownership, offline policy checks and costed gateway plan reviewed before apply; one resource/state owner.

## P4 — Validate Dynatrace Managed compatibility

- **P4.1 Confirm Managed entitlement and supported configuration** (waiting_for_decision). Acceptance: Licence/installer, cluster/agent compatibility, vendor sizing/OS/storage, connectivity, retention and cost envelope confirmed.
- **P4.2 Provision and configure supported Managed backend** (planned). Acceptance: Licensed backend on supported dedicated hosts is installed/configured through documented reproducible steps.
- **P4.3 Validate native and selected custom instrumentation** (planned). Acceptance: Separate native/custom cohorts validate endpoints, auth, enrichment, retention and duplicate spans for each signal.
- **P4.4 Build supported views and tested compatibility matrix** (draft). Acceptance: Supported dashboards/alerts/read APIs and exact versions recorded; reference enterprise environment gaps and SaaS-only features explicitly labelled.

## P5 — Add bounded investigation agents

- **P5.1 Define synthetic status tools and incident fixtures** (planned). Acceptance: Allowlisted health/version/failure schemas and versioned synthetic incidents have expected outcomes.
- **P5.2 Implement bounded service-status investigation agent** (planned). Acceptance: Retries/steps/tools/time bounds and injected failure cases pass; token bounds are verified only when live provider is authorized.
- **P5.3 Implement profile-specific read-only monitoring adapter** (planned). Acceptance: Bounded local evidence reads pass; live Managed adapter additionally requires P4.4 evidence; unrestricted queries/writes are absent.
- **P5.4 Validate evidence-citing read-only SRE copilot** (planned). Acceptance: Timeline, causes, evidence IDs, uncertainty and human checks pass versioned incident tests; untrusted text cannot add write/shell tools.
- **P5.5 Implement governed model adapter and bounded gateway behavior** (planned). Acceptance: Deterministic mode preserved; gateway-scoped identity contract, model allowlist and typed auth/rate/quota/timeout errors pass synthetic checks; retries and streaming bounded; no direct-endpoint fallback. Actual cloud/live claims require P3.5 and G5.

## P6 — Experiment, demonstrate and hand over

- **P6.1 Define comparison cohorts and acceptance measurements** (planned). Acceptance: Matched load, expected graphs, baselines, versions and measurement scripts defined before experiments.
- **P6.2 Run coverage, overhead, outage, redaction and rollout experiments** (planned). Acceptance: 100-request coverage, duplication/loss, p95 overhead, outage recovery and zero-prohibited-value results recorded with limitations.
- **P6.3 Run authorized live-model evidence and optional triage replays** (planned). Acceptance: Real provider timing/available usage, dated pricing and model bounds recorded; optional three-replay triage evidence labelled exploratory.
- **P6.4 Rebuild from releases and prepare demonstration/report** (planned). Acceptance: Pinned checkout reproduces demo; presentation/report state costs, compatibility, measured outcomes and outstanding limitations.
- **P6.5 Complete scoped cleanup and evidence handover** (planned). Acceptance: Reviewed dedicated-scope teardown verified, remaining resources inventoried and sanitized evidence/lifecycle instructions handed over.
- **P6.6 Validate APIM governance, safe telemetry and scoped lifecycle** (planned). Acceptance: Versioned gateway cohort defined before execution; live authorized/denied calls, token-rate/quota bounds, bypass denial, faults, available usage, privacy canaries, correlation/overhead, rebuild and scoped cleanup evidenced; no Managed parity claim.
