# What remains

Updated: 2026-10-29T01:05:24+04:00 (Asia/Dubai).

Execution: **Plan accepted; follow task gates**.

Next action: select a ready step from POC_TRACKER.md.

## P1 — Prove the local vertical slice

- **P1.1 Review existing draft code, dependencies and gaps** (draft). Acceptance: Draft review records corrections, supported versions and treatment of the deprecation/incomplete CI input.
- **P1.2 Validate API and retrieval contracts** (draft). Acceptance: Schemas and examples validate; authentication, outcomes and bounds agree with intended behavior.
- **P1.3 Complete synthetic policy workload and adapter** (draft). Acceptance: Real HTTP tool path and versioned expected-answer dataset pass; mock usage is explicitly unknown.
- **P1.4 Validate propagation and metadata-only telemetry** (draft). Acceptance: Service/version identity, exact span graph, low-cardinality metrics and content-capture boundaries are tested.
- **P1.5 Prove local backend runner and lifecycle** (draft). Acceptance: Working chosen runner starts/stops owned services; backend readiness and ephemeral retention are documented.
- **P1.6 Record complete local trace and exported-data evidence** (planned). Acceptance: Fresh run saves machine-readable results, backend trace graph and canary checks against exported telemetry; bounded failure is demonstrated.

## P2 — Establish personal GitHub delivery

- **P2.3 Complete reproducible CI, contract tests and builds** (draft). Acceptance: Required locks exist; clean-checkout CI and image build pass; immutable actions and restricted PR permissions verified.
- **P2.4 Pin image digests and multi-repository release manifest** (planned). Acceptance: Known commits/releases and immutable images reproduce the local demo; scoped coordination credentials are documented.

## P3 — Plan and deploy personal Azure

- **P3.1 Confirm personal Azure targets, region and budget** (waiting_for_decision). Acceptance: Supplied exact tenant/subscription and personal identity are matched; region/budget/currency and model requirement recorded.
- **P3.2 Produce costed Azure HLD and runner/network design** (draft). Acceptance: Component active/idle costs, retention, AKS/runner reachability and optional Managed footprint are documented using dated inputs.
- **P3.3 Prepare Terraform, state bootstrap and scoped OIDC** (planned). Acceptance: IaC validates with provider locks; private state ownership, scoped RBAC/federation, actual OIDC subject and resource tags are verified.
- **P3.4 Review concrete IaC plan and authorize spending scope** (waiting_for_decision). Acceptance: Concrete plan, cost assumptions, resource scope and lifecycle presented and authorized once for the agreed bounds.
- **P3.5 Deploy pinned Azure baseline through GitHub Actions** (planned). Acceptance: Only authorized resources deploy; workflow, smoke, telemetry and cloud-mock release evidence saved.
- **P3.6 Verify cloud start/stop and scoped destroy/recreate** (planned). Acceptance: Owned lifecycle works for exact scope; remaining stopped-resource costs/state and evidence retention documented.

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

## P6 — Experiment, demonstrate and hand over

- **P6.1 Define comparison cohorts and acceptance measurements** (planned). Acceptance: Matched load, expected graphs, baselines, versions and measurement scripts defined before experiments.
- **P6.2 Run coverage, overhead, outage, redaction and rollout experiments** (planned). Acceptance: 100-request coverage, duplication/loss, p95 overhead, outage recovery and zero-prohibited-value results recorded with limitations.
- **P6.3 Run authorized live-model evidence and optional triage replays** (planned). Acceptance: Real provider timing/available usage, dated pricing and model bounds recorded; optional three-replay triage evidence labelled exploratory.
- **P6.4 Rebuild from releases and prepare demonstration/report** (planned). Acceptance: Pinned checkout reproduces demo; presentation/report state costs, compatibility, measured outcomes and outstanding limitations.
- **P6.5 Complete scoped cleanup and evidence handover** (planned). Acceptance: Reviewed dedicated-scope teardown verified, remaining resources inventoried and sanitized evidence/lifecycle instructions handed over.
