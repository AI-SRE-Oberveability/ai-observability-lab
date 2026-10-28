# Personal Azure AI Agents and Observability POC — delivery plan

Prepared: 28 October 2026, Asia/Dubai. Status: **approved by the user; initial public publication in progress**.

The immediate deliverable is this plan, a maintained high-level design (HLD), and an automated progress tracker. The user has accepted the plan and authorized public-source review and pushes to all four repositories; cloud spending retains its separate gates. Previously created local files are retained as drafts and assessed against the plan; they do not imply acceptance or deployment.

Confirmed choices: Terraform for Azure IaC; four repositories under personal GitHub owner `javedkumail`; GitLab credentials preserved; tracker updates after each work step; continuous HLD/current/next/remaining updates. The user created all four repositories as public; their existence and empty contents were verified on 28 October 2026. Source review and initial pushes remain pending. [Engineering standards](docs/engineering-standards.md) are part of every work package's definition of done.

## 1. Outcome and boundaries

Build a reproducible personal lab that demonstrates observability **of AI** and read-only **AI for observability**. Three use cases remain distinct: synthetic policy assistant, synthetic service-status investigator, and evidence-citing SRE copilot. Dynatrace Managed is the preferred compatibility target for the reported reference enterprise environment environment, subject to entitlement and supported sizing/version checks.

Use only invented documents, requests, incidents and telemetry. Confirm the exact personal Azure tenant/subscription and GitHub owner before using either account. Customer systems and prior customer artifacts are outside the lab. The initial private recommendation is superseded by the user-created public repositories; review source for public publication before the first push. Local/mock evidence, live-model evidence, Azure evidence and Managed/SaaS results must be labelled independently.

## 2. Starting position

- Existing study files are outside the new `personal-ai-observability` directory.
- Four proposed repository directories, initial contracts, Python draft services, telemetry configuration and documentation were created before this plan was agreed.
- An observed local run completed with **18 tests passing and one deprecation warning**. It exercised local HTTP and in-memory telemetry assertions. This is historical evidence; there is no stored JUnit result from that run.
- The pinned Collector configuration passed its CLI validation. Windows Collector/Jaeger archives were downloaded and checksum checked. A running Collector-to-Jaeger demonstration was not completed.
- Docker's engine was unreachable. Workload CI is an inactive draft under `.github/workflow-drafts` and references a missing `requirements-dev.lock.txt`; it has not run on GitHub.
- The user has now created four public, empty GitHub repositories; exact destinations are in docs/repository-layout.md. No local push, Azure identity/resource, live model deployment or Dynatrace environment has been created. Azure targets, budget and Managed entitlement remain unknown.

## 3. Milestones and order

Effort ranges below are planning estimates in focused working days, **not calendar commitments or cloud cost estimates**. They will be revised after the local review and each stage exit. External account access, licence delivery, quota and vendor lead time are excluded.

| Phase | Deliverable | Depends on | Indicative effort | Exit decision |
| --- | --- | --- | --- | --- |
| P0 — Agree the plan | Scope, HLD, tracker, decisions and current-state inventory | Current workspace | 0.5–1 day | User accepts scope and sequence |
| P1 — Prove the local slice | Repeatable policy assistant, real HTTP tool, mock model and Collector/Jaeger evidence | P0 acceptance | 2–3 days | Local demo and data-capture checks pass |
| P2 — Establish GitHub delivery | Four verified repositories, reproducible CI/builds and pinned release manifest | Repository setup can follow P0 alongside P1; CI/release completion needs P1 | 1–2 days | Clean checkout builds/tests; ownership clear |
| P3 — Plan and deploy personal Azure | Costed IaC, bootstrap, OIDC and scoped AKS delivery | P2; exact personal targets, region and budget | 2–4 days | Authorized scope deploys and tears down reproducibly |
| P4 — Validate Managed compatibility | Licensed/supported Managed backend and compatible agent/OTel configuration | P3; entitlement, approved sizing/version | 2–4 days plus vendor lead time | Signal-by-signal evidence and compatibility matrix |
| P5 — Add investigation use cases | Bounded status agent and read-only evidence-citing SRE copilot | P1/P2 baseline; selected backend validated | 2–4 days | Fault bounds, evidence references and read-only policy pass |
| P6 — Run experiments and hand over | Acceptance report, demo, rebuilt lab and verified lifecycle | P3–P5 | 2–3 days | Findings, limitations, cost basis and cleanup accepted |

P5 design and synthetic fixtures can be prepared locally before Managed access arrives **after plan acceptance**. A vendor delay must not cause SaaS to silently replace Managed. Optional SaaS comparison is a separately chosen side experiment after P1, with its own entitlement, expiry and result labels.

## 4. Step-by-step work packages

The task IDs below match the tracker. Each task has an owner, dependencies, artifacts and acceptance criteria in `tracking/plan.json`. Codex handles engineering work after authorization. The user supplies account decisions, budget and entitlement; secure credential entry stays in supported authentication/secret mechanisms.

### P0 — Establish the agreed baseline

1. **P0.1 Inventory:** preserve existing work, list drafts, known validations and unverified claims.
2. **P0.2 Plan and HLD:** record system boundaries, repository ownership, deployment profiles, decision gates and remaining work.
3. **P0.3 Tracker:** implement event-driven updates after each work step, including evidence, blockers and changed-source detection.
4. **P0.4 Review:** obtain explicit acceptance or requested changes. Until then, stop at planning and tracker maintenance.

### P1 — Prove one local vertical slice

1. **P1.1 Review drafts:** inspect the existing contracts/services, select supported dependency versions and list corrections. Resolve the test-client deprecation and incomplete CI input when appropriate.
2. **P1.2 Contract:** agree authentication, `/v1/ask`, typed outcomes, tool schema and bounded errors before further code changes.
3. **P1.3 Workload:** complete the synthetic policy service, deterministic adapter and separate retrieval tool. Version the invented policy/answer fixtures.
4. **P1.4 Telemetry contract:** fix service/version/environment attribution, W3C propagation, exact expected span graph, low-cardinality metrics and metadata-only capture.
5. **P1.5 Backend and runner:** choose the working local runner. Prefer Compose if Docker becomes available; verify the pinned native Windows alternative otherwise. Provide start, stop and cleanup instructions.
6. **P1.6 Evidence:** rerun against recorded versions, save machine-readable results, prove cross-service span edges and absence of prohibited fixture values **in exported telemetry**, and retrieve the trace from Jaeger. A successful API response is insufficient.

P1 exit: a fresh local setup reproduces a cited answer and a bounded failure; traces reach the backend; known capture-policy tests pass. No claim of real LLM usage, OneAgent enrichment or Managed parity is made from this stage.

### P2 — Create the repository and CI foundation

1. **P2.1 Targets:** record owner `javedkumail`, the four actual public destinations and account/plan constraints.
2. **P2.2 Repositories:** the user has created four empty public repositories. Inspect their current contents, review source for publication, initialize each local source folder independently and push reviewed source/drafts, keeping their validation status explicit. Preserve GitLab credentials; keep the parent workspace and original handoff outside automatic publication. This source-storage step can run alongside P1; it does not require a finished POC.
3. **P2.3 CI:** complete locked test/build dependencies, contract checks, meaningful tests and immutable action references. Give untrusted PRs no deployment identity.
4. **P2.4 Releases:** build immutable images, record digests, pin each repository's commit/release in the lab manifest and define cross-repository coordination using scoped credentials.

P2 exit: a clean checkout/release manifest reproduces the local demo and CI evidence. GitHub Actions execution is evidenced separately from local execution.

### P3 — Personal Azure design, cost and deployment

1. **P3.1 Targets:** confirm exact personal tenant/subscription, region, monthly budget/currency, model requirement and quota. Match the authenticated identity to those supplied values.
2. **P3.2 Costed HLD:** choose AKS/networking, registry, secret delivery, retention and runner connectivity. Estimate active/idle cost by component, including optional Managed infrastructure separately.
3. **P3.3 IaC/bootstrap:** use the user-selected Terraform stack: modules, provider locks, formatting/validation/lint/security checks, protected remote state/bootstrap ownership, scoped OIDC/RBAC, tags and bounded resource groups. Verify the actual GitHub OIDC subject and runner reachability.
4. **P3.4 Plan review:** present concrete Terraform changes, cost assumptions and lifecycle scope for authorization before spending.
5. **P3.5 Deploy/validate:** provision only authorized scope through GitHub Actions; deploy pinned monitoring/application releases and save smoke/telemetry evidence.
6. **P3.6 Lifecycle:** prove supported start/stop and scoped destroy/recreate behavior. Inventory charges that remain while compute is stopped.

P3 exit: cloud mocked evidence is reproducible from code and workflows. A live Azure model test is a separately recorded cohort with actual available token usage and a dated pricing basis. Missing usage remains unknown.

### P4 — Managed compatibility

1. **P4.1 Prerequisites:** confirm installation/licence entitlement, cluster version, OS/node/disk/IOPS sizing, compatible OneAgent/ActiveGate/Operator, DNS/TLS/networking, retention, backup/upgrade method and cost envelope.
2. **P4.2 Backend:** after the gate is satisfied, provision dedicated supported hosts and automate supported installation/configuration. Installing an Operator on AKS does not install a Managed backend.
3. **P4.3 Instrumentation:** compare OneAgent native coverage and only the missing custom spans in separate cohorts. Validate each OTel signal's endpoint, auth, enrichment and retention. Check duplicate spans explicitly.
4. **P4.4 Views/matrix:** implement supported dashboards/alerts/APIs and record tested versions, exclusions and the gap to the reported reference enterprise environment deployment. Do not assume SaaS AI apps, Grail, DQL or MCP support on Managed.

P4 exit: each supported claim has evidence from the actual licensed Managed profile. If entitlement is unavailable, this stage remains blocked while authorized local work can continue.

### P5 — Bounded status agent and read-only SRE copilot

1. **P5.1 Status contracts/fixtures:** health, deployment version and recent synthetic failure tools, with a small allowlist and versioned scenarios.
2. **P5.2 Status agent:** enforce maximum steps/tool calls/retries/time and, when a live provider exists, actual token budgets. Exercise latency, timeout, 429/5xx, malformed response and broken dependency.
3. **P5.3 Monitoring adapter:** define bounded metrics/problem/event/log-summary reads per backend. Use verified Managed APIs; isolate any SaaS-only query adapter. No arbitrary queries or writes.
4. **P5.4 SRE copilot:** produce incident timeline, likely causes, evidence IDs, uncertainty and suggested human checks. Treat documents/logs as untrusted data. Verify no shell, Azure/Kubernetes write or automatic remediation capability.

P5 exit: the tool loop terminates under faults; SRE statements cite the retrieved evidence and expose missing evidence. Local fixtures do not count as live-backend validation.

### P6 — Experiments, demonstration and teardown

1. **P6.1 Experiment design:** define matched cohorts, load, expected graphs, versions, acceptance thresholds and measurement scripts before running comparisons.
2. **P6.2 Observability evidence:** run 100-request coverage cohort, duplication/loss checks, broken propagation, Collector/backend outage, redaction and rollout/version attribution tests. Measure overhead separately.
3. **P6.3 Live/provider and triage evidence:** test real model behavior if authorized; reconcile available usage with billing. Optionally run three exploratory incident replays with/without the assistant.
4. **P6.4 Rebuild/demo:** rebuild from pinned repositories, demonstrate all use cases, prepare a concise presentation and findings report with compatibility/cost limitations.
5. **P6.5 Cleanup/handover:** run reviewed scoped teardown, inventory remaining billable resources/state, retain sanitized evidence and hand over exact run/lifecycle instructions.

## 5. Acceptance targets

| Target | Measurement | Stage |
| --- | --- | --- |
| Trace coverage >=95% of 100 selected synthetic requests | Expected names, multiplicity, service identity and parent/link graph compared with backend observations | P6 |
| No missing/duplicate spans in healthy controlled baseline | Trace-graph evidence; loss in fault cohorts measured separately | P1/P6 |
| <5% p95 overhead, or explicitly accepted measured tradeoff | Matched baseline/instrumented load and documented resources | P6 |
| Zero prohibited fixture values exported | Inspect exported spans/metrics/logs for controlled canaries; state exact capture surface tested | P1/P6 |
| Reproducible build and lifecycle | Clean checkout, pinned manifest/images, real start/stop/destroy evidence | P2/P3/P6 |
| Grounded and bounded agent behavior | Versioned expected-answer and fault datasets; citations, uncertainty and execution bounds | P1/P5 |
| Optional 20% lower median triage time across three replays | Exploratory result only; no statistical proof claim | P6 optional |

## 6. Decisions and dependencies

| Gate | Required decision | Needed before |
| --- | --- | --- |
| G0 | Accept/revise this plan and HLD | Resume implementation |
| G1 | Verify exact personal GitHub destinations and actual visibility | Repository creation or push |
| G2 | Confirm exact personal Azure targets, region and budget | Account-specific cloud design/operations |
| G3 | Authorize concrete IaC scope and cost envelope | Azure deployment/spend |
| G4 | Confirm Managed entitlement, version, sizing and cost | Managed provisioning/integration |
| G5 | Approve model deployment/quota and bounded live usage | Paid/live-provider experiments |

Do not request all account information now. Request it when the next accepted step needs it. Never ask for tokens/passwords in chat. Earlier authorization remains valid within its agreed scope; gates record decisions and do not cause repeated approval requests.

## 7. Working rhythm and HLD updates

After **each work step**, record the outcome/evidence and refresh `POC_TRACKER.md`. Update `HLD.md` when boundaries, components, telemetry paths or deployment choices change. Every user-facing progress update states: current HLD, what changed, next step and what remains. If no architecture changed, say so briefly and identify the next boundary being validated.

Tracker updates are event driven, as requested. There is no daily schedule or background deployment. A refresh inventories artifacts and detects stale evidence; file presence cannot prove backend ingestion, cloud deployment or answer quality. Preserve failed results and label observed historical results explicitly.

Immediate next step: complete the authorized source review and initial pushes. G0 and G1 are accepted. The next implementation package is P1.1: review the existing drafts against the local acceptance criteria; cloud spending remains separately gated.
