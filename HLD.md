# High-level design — current, target and remaining work

Version: 0.21 Linux feature publication verified. Updated: 8 November 2026, Asia/Dubai. Execution: **independently reviewed Linux proof published on feature branch; exact-source branch CI passed; no main merge or Azure execution**.

## Purpose

Provide three synthetic use cases: a policy assistant, a service-status agent and a read-only SRE copilot. Observe AI workload behavior separately from using AI to investigate monitoring evidence. Use personal Azure/GitHub targets; preserve Dynatrace Managed as the preferred later compatibility profile.

Confirmed implementation choices: **Terraform owns Azure infrastructure**, Helm/Kubernetes manifests own workload/observability deployments, and four repositories under `AI-SRE-Oberveability` separate resource ownership. The organization is owned by the personal account `javedkumail`. All four transferred repositories retain their IDs, published commits and public visibility. The infrastructure destination is `AI-Observability-Infra`; other names match the source folders. Reviewed source is published to all four repositories; initial commit receipts are recorded below. GitLab credentials remain intact. Engineering standards are defined in `docs/engineering-standards.md`.

## Verified local deterministic slice

```mermaid
flowchart LR
  T[Synthetic caller] --> A[Policy agent]
  A --> M[Deterministic model]
  A -->|Real HTTP and W3C context| R[Retrieval service]
  R --> D[Synthetic documents]
  A -->|OTLP HTTP| C[Loopback Collector]
  R -->|OTLP HTTP| C
  C -->|OTLP gRPC| J[Jaeger memory backend]
  C --> P[Prometheus exposition]
```

The Windows loopback profile now has actual backend evidence: the healthy request produced exactly seven spans across two services with expected parents; a synthetic dependency 503 returned tool_error after two attempts. Collector file exports, queried Jaeger data, metric surfaces and controlled operation logs passed canary checks. Resource service/version/environment identity was checked. All owned listeners stopped; Jaeger restart returned 404 for the prior trace. See evidence/local-backend-proof.json and docs/local-backend-runbook.md.

All 18 workload tests pass without the previous TestClient warning. This is one deterministic healthy/fault cohort, not live model, P6 coverage/overhead, durable delivery, Compose, Azure or Managed proof. The native runner uses a pinned internal Jaeger read API for this bounded proof; production read adapters remain separate.

## Proposed AKS and Azure AI target

[Editable architecture board](https://www.figma.com/board/JxOlJjtrEmIFrhRU8ltID0) and [implementation plan with all three views](docs/architecture/README.md).

![Selected AKS and Citadel/APIM target with official Azure icons](docs/architecture/azure-governance.png)

[Editable draw.io](docs/architecture/azure-governance.drawio) | [SVG preview](docs/architecture/azure-governance.svg) | [Governance plan](docs/architecture/governance-plan.md). Six unchanged official Microsoft Azure icons are embedded; custom agents/tools use neutral shapes.

AKS hosts separate policy/status/SRE Deployments, bounded tool APIs and the Collector. Approved live model calls pass through a separate Azure APIM service implementing the selected Citadel-inspired governance boundary. Per-service AKS Workload ID supplies gateway-scoped pod identity; APIM managed identity supplies scoped model access. GitHub OIDC remains a separate deployment identity boundary. Governed agent identities receive no direct model-inference role. Proposed namespaces are ai-lab, observability and experiments. Helm/manifests remain with their owning workload/monitoring repositories; Terraform owns new Azure infrastructure and scoped identity/state.

The user selected an **optional existing Azure AI project reuse path**. Candidate Foundry/OpenAI endpoints, project resources, Search/Blob, ACR/Key Vault or AKS are referenced only after personal ownership, compatibility, quota, networking and cost are verified. No resource inventory, migration, import or adoption has occurred. Custom agent runtimes stay on AKS; a Foundry-hosted agent would be a separate comparison profile.

The first cluster cohort retains the deterministic model and bundled synthetic documents. Approved live-model and optional RAG cohorts follow later. Blob/Search, Prometheus storage and the expanded platform modules are proposed additions. The current Terraform code still covers one resource group; full AKS/ACR/Key Vault/networking and release deployment remain to implement.

Native OneAgent telemetry follows its supported route independently of the arbitrary Collector. Managed remains a licensed, version/sizing-gated backend on supported hosts. Read-only SRE adapters use only bounded, verified backend reads. No SaaS-specific feature is assumed on Managed.

Personal targets/region/budget, node/storage/network/runner sizing, retention, model quota and active/idle costs remain open. This diagram records the intended design, not deployed resources or cloud authorization.

## Read-only SRE path — planned

```mermaid
flowchart LR
  I[Synthetic incident] --> S[SRE copilot]
  S --> A[Bounded read-only adapter]
  A --> B[Selected lab monitoring backend]
  B --> E[Allowlisted evidence with IDs and timestamps]
  E --> S
  S --> H[Human review of timeline, causes and uncertainty]
```

The adapter cannot execute arbitrary queries, shell commands or Azure/Kubernetes writes. Managed uses verified supported APIs; SaaS-only DQL/Grail, if selected, has separate configuration. Monitoring text is untrusted data. Every substantive claim references evidence or declares uncertainty.

## Nonfunctional design

- Operational metadata is the default capture policy; prompts, completions, documents, arguments and secrets stay out of telemetry.
- Fixed service/environment/version identity and W3C context enable cross-service trace validation. Metrics avoid user/conversation/trace labels.
- Execution and telemetry queues/retries are bounded. Mock token usage stays null; actual token budgets and dated cost estimates require a live provider.
- Synthetic load, short retention, explicit lifecycle commands and scoped IaC contain lab consumption. Budget notifications are not a guaranteed spending cutoff.
- Local, cloud, live-provider, Managed and optional SaaS evidence is labelled independently.

## HLD change log and next boundary

| Version | Change | Validation state |
| --- | --- | --- |
| 0.1 | Documented existing drafts, proposed Azure/Managed target and separate SRE evidence path | Plan awaiting user review |
| 0.2 | Confirmed Terraform, four private repositories under javedkumail, GitLab coexistence, event-driven tracker and engineering standards | User choices recorded; implementation still paused |
| 0.3 | Verified four public, empty GitHub destinations created by the user; recorded exact infrastructure name | Read-only API evidence saved; no push or architecture boundary change |
| 0.4 | User approved the plan and public pushes; review sanitizes reference-environment names and fixes repository-local evidence links | Review passed: 18 workload tests, 11 tracker tests, zero staged secret findings; GitLab credentials preserved |
| 0.5 | Organization created; all four public repositories transferred and local remotes updated | IDs/history/ownership verified; organization documentation pushed to all four repositories |
| 0.6 | Shared Project #1 links all four repositories and mirrors 36 task issues through event-driven synchronization | Live task/link/view checks and 20 tracker/sync tests passed; source/cloud validation boundaries unchanged |

**What we are going to do next:** prepare and validate a release candidate pinned to the four tested main commits. Keep the missing workload registry digest explicit, then review the candidate before selecting/publishing an image artifact.

**What remains:** immutable workload image publication and replay; release pinning acceptance; personal Azure targets/budget and costed platform/APIM IaC; Managed compatibility; status/SRE agents; live-provider/comparison experiments; demo/rebuild and cloud teardown.

After every work step the tracker supplies current status, next executable work and remaining decisions. Update this HLD whenever a component, boundary, ownership rule or telemetry path changes.

<!-- publication-progress -->

## Verified source publication

| Repository | Initial reviewed commit | Status |
| --- | --- | --- |
| ai-observability-infra | `b21c746acac6` | Pushed and verified |
| ai-agent-workloads | `6fc332a2cddf` | Pushed and verified |
| ai-observability-config | `9d81a64e0fea` | Pushed and verified |
| ai-observability-lab | `0d5cf9f01db8` | Pushed and verified |

The lab receipt pins the initial reviewed source commit; later coordination updates are descendants. Initial source publication alone did not establish backend delivery, CI execution or cloud/Managed deployment; later CI evidence is recorded separately. Component ownership is unchanged.

## Organization migration status

`AI-SRE-Oberveability` is created on GitHub Free, and authenticated membership verifies javedkumail as active owner. 4/4 repositories have transferred with IDs, commits and public visibility preserved. [Shared Project #1](https://github.com/orgs/AI-SRE-Oberveability/projects/1) is verified with 41 unique task issues, all four repository links, Delivery board and All tasks views. GitLab credentials and global Git helpers remain unchanged.

| Repository | Actual owner | Transfer verification |
| --- | --- | --- |
| AI-Observability-Infra | AI-SRE-Oberveability | transferred_and_verified |
| ai-agent-workloads | AI-SRE-Oberveability | transferred_and_verified |
| ai-observability-config | AI-SRE-Oberveability | transferred_and_verified |
| ai-observability-lab | AI-SRE-Oberveability | transferred_and_verified |

Organization grouping changes repository ownership and future OIDC inputs, not component responsibilities. Verify the actual new owner/repository OIDC subject before configuring Azure federation. No Azure federation was deployed before this move.

## Project setup continuation — 29 October 2026

The existing organization Project #1 was completed after browser reconnection and verified as AI SRE Observability POC. Project-capable authentication is verified as javedkumail with the user-approved project scope; no duplicate Project was created. The CLI uses isolated local configuration, and Git authentication setup was declined. Existing GitHub repository authentication remains available; no GitLab credential/global helper changes were made.

## Shared Project tracking design

Project #1 is shared across the four repositories. Managed issues mirror task acceptance, dependencies, gates and evidence; Project fields expose task ID, phase, responsible owner and exact evidence status. The board summarizes Todo/In Progress/Done. Synchronization is event driven after local work-step recording via scripts/sync_github_project.py --apply; there is no scheduled job. New authentication is limited to the separately approved GitHub CLI scope and does not alter GitLab credentials or global Git helpers.

The Project retains private visibility for authorized organization members. Public repository source and sanitized evidence remain public. Local plan/state are authoritative; human notes outside managed issue blocks are preserved. Draft, blocked and pending decisions remain distinct in Evidence status. A task moves to Done and its issue closes only when the local tracker accepts its evidence. Live verification checks issue identity/state, all managed fields, and repository links. Interrupted synchronization resumes from saved task mappings and discovers existing managed issues to avoid duplicates. See evidence/shared-project-completion.json for the setup receipt and evidence/shared-project-verification.json for the latest synchronization result.

## Actions implementation boundary — 29 October 2026

The user authorized four independent CI workflows plus guarded Terraform delivery. Current status: planning complete; implementation and GitHub runs pending. CI stays read only. Manual Terraform plan/apply will use separate protected environments and OIDC; the initial root covers only a tagged resource group. Cloud execution stays disabled until personal targets, budget, state and scoped identities are confirmed. No AKS/Managed resource or Azure identity is created in this setup. See docs/actions-delivery-plan.md. Next: implement CI, validate Terraform/guards, publish PRs, then capture actual workflow conclusions.

### Actions step 2 — source checks and protected environment setup

Four CI definitions now exist on review branches. A fresh hash-locked workload environment passed 18 tests (one existing test-client deprecation warning); tracker tests passed 20/20; deployment guard tests passed 11/11. Five workflow definitions passed actionlint after correcting context availability. Config source checks passed; Docker build/Collector validation await hosted CI. Terraform provider initialization succeeded; cross-platform locking and final Terraform validation are still being checked.

Both infra environments, azure-lab-plan and azure-lab-apply, are verified main-only with owner review and administrator bypass disabled. The repository deployment flag is false; no Azure values, identities or roles were configured. GitHub reports an immutable OIDC subject prefix using organization/repository IDs; actual environment token/federation validation remains an Azure bootstrap prerequisite. Next: finish Terraform checks and reviewed PR publication, then capture real CI results.

### Actions step 3 — Terraform validation and review publication

Terraform foundation validation passed with AzureRM 5.11.0, and both mocked invalid-scope/expiry tests passed. Eleven Python safety tests cover disabled execution, branch/repository restrictions, target/context checks, reviewed-plan binding and destructive/scope-expanded plan rejection. Windows provider communication required a retry outside the restricted execution sandbox; no Azure login or cloud plan was run. Cross-platform package locking is still being collected; signed registry archive checksums already exist in the lock. Workload and observability PRs are open and hosted CI is running. Publication checks excluded generated Python cache files before the infra push. Next: complete all four PR checks and capture main-branch results; Azure execution stays disabled.

### Actions step 4 — all four PR pipelines validated

All four implementation PRs passed hosted CI. Workloads passed 18 tests and built its container; observability passed Compose and the real Collector validator; lab passed 20 tracker/sync tests; infra passed 11 safety tests, strict backend-disabled Linux init/validate and two mocked Terraform scope tests. The Linux lock mismatch was fixed by generating its real package hash from an official archive verified against signed registry metadata; strict readonly checks remain enabled. No cloud authentication or provisioning ran. See evidence/actions-pr-validation.json and evidence/actions-provider-lock-review.json.

The automatic approval review rejected merging workload PR 9 because explicit merge authorization was not present. At this review stage the PRs remained open. The user subsequently approved the four merges and final tracking receipt update; main CI and the live disabled-dispatch check are now verified in step 5 below. Both protected infra environments are verified main-only with owner review and no administrator bypass. AZURE_DEPLOYMENT_ENABLED remains false. No Azure target values, roles or identities were added. Source and global Git configuration checks preserve GitLab access.

```mermaid
flowchart LR
  PR[Four repository PRs] --> CI[Read-only CI: tests/build/config/Terraform]
  CI --> R[Explicit merge approval]
  R --> M[Main branch workflows]
  M --> D[Manual dispatch and deployment-enabled guard]
  D -.->|G2/G3 and bootstrap still pending| E[Protected plan/apply environments]
  E --> O[Separate OIDC identities]
  O --> S[Dedicated protected Blob state]
  S --> P[Private Terraform plan and review fingerprint]
  P --> A[Matching saved-plan apply: one resource group]
```

### Actions step 5 — verified activation after approved merges

The user explicitly approved the four named PR merges and the final HLD/tracker-only receipt update. All four PRs merged at their verified tested heads. All four resulting main-branch CI runs succeeded: workload tests/container build; observability source/Compose/Collector validation; lab tracker/sync tests; infra lint, 11 safety tests, strict locked Terraform initialization/validation and two mocked scope tests. The final documentation-only receipt PR is subject to the same CI checks.

The manually dispatched Terraform plan was intentionally tested with AZURE_DEPLOYMENT_ENABLED=false. It failed at the named preflight guard with the expected disabled-execution message; the entire Terraform job was skipped and Azure login did not run. This expected rejection is safety verification, not a failed Azure deployment. No target IDs, credentials, Entra identities, role assignments or Azure resources were created. GitLab credentials and global Git configuration remain unchanged. Exact source/run/merge evidence is in evidence/actions-main-activation.json and evidence/actions-disabled-deployment-verification.json.

**Current delivery boundary:** CI is active in all four repositories; manual Terraform plan/apply code and protected environments are configured. Actual Azure execution remains disabled pending G2/G3, state bootstrap, separate scoped plan/apply identities and verification of environment-specific immutable OIDC claims. The concrete Terraform root currently owns one tagged resource group. AKS/platform resources, registry publication, workload rollout, local backend proof, Managed and live models remain later work.

## Architecture step — 29 October 2026

Three editable diagrams now cover the AKS application target, telemetry/read-only SRE profiles and the CI-to-Terraform-to-AKS implementation sequence. The implementation guide defines namespace/resource ownership, separate runner/pod identities, optional existing-resource checks, cost/access gates and stage exits. The user chose an optional Azure AI reuse path; no existing cloud project is assumed available. The current accepted count remains 11/38: diagram completion does not close P1 backend, P3 cost/deployment, Managed or live-model tasks.

**Next implementation:** prove the local policy/telemetry slice, then confirm personal Azure targets and costs; build bootstrap/platform Terraform and image/release/Helm delivery before any approved AKS deployment. See docs/architecture/README.md for the full sequence and public design references. GitLab credentials and global Git configuration remain unchanged.

## Historical Citadel reference review — 1 November 2026

The later selection below supersedes the optional-only recommendation in this review; the review remains historical evidence.

Reviewed the user-provided [Citadel lab](https://microsoftlearning.github.io/mslearn-ai-governance/lab/) and its workshop/upstream documentation. The [fit review and proposed adoption sequence](docs/architecture/citadel-governance-review.md) records APIM as an optional governance experiment around approved live model calls. AKS remains the proposed custom-agent runtime, with separate OTel/backend and bounded read-only SRE paths. Terraform remains the sole Azure resource owner.

No gateway component, SKU, cloud scope or upstream code was adopted. Existing resource reuse stays optional and unverified. Privacy, source-version, networking, identity, cost and teardown differences must be resolved before implementation. Current diagrams retain the agreed baseline; a gateway view follows only if that experiment is selected.

**Next:** P1.1 local draft review, then real backend proof. **Remaining:** G2 personal targets/region/budget, G3 costed scope authorization, G4 Managed entitlement/compatibility, G5 live model/quota approval; platform Terraform, AKS delivery and experiments. The architecture proposal remains in PR #21; Azure execution remains disabled.

## Citadel/APIM selected in the target — 1 November 2026

The user requested inclusion of governance in the architecture and execution plan. [Three current views and retained baseline](docs/architecture/README.md) and the [governance work plan](docs/architecture/governance-plan.md) now cover AKS agents -> APIM outside AKS -> an approved new or verified existing Foundry/OpenAI model endpoint. This is design selection; resource sizing, costs and cloud execution remain unapproved.

Terraform owns APIM, backend/access inventory, identities, network/DNS, diagnostics and versioned XML policy fragments. Workloads own the governed adapter and bounded error/retry behavior; observability-config owns capture/correlation requirements; lab owns experiments and evidence. The application keeps tool/time bounds and read-only SRE controls. Gateway diagnostics follow an Azure Monitor route independently of the Collector; no trace continuity or supported Managed result is inferred from this drawing.

P3.7 tracks governance IaC before the concrete combined plan review; P5.5 tracks the gateway adapter; P6.6 tracks gateway/privacy/lifecycle evidence without making Managed a prerequisite. The shared plan now has 41 tasks, with 11 accepted deliverables. The earlier baseline remains labelled on the board and under docs/architecture/baseline-2026-10-29.

**Next:** finish P1.1 and local backend proof. **Remaining:** G2 targets/region/budget, costed AKS/APIM design and protected state/OIDC; G3 scope authorization; Terraform platform/gateway and AKS release; G5 live usage and governed validation; G4 Managed compatibility and later SRE/experiments. Azure deployment remains disabled and GitLab credentials/global configuration remain intact.

The user also selected a draw.io companion using official Azure icons. Its editable source, standalone SVG/PNG and icon provenance/rights notice are published with this design. The original FigJam views remain labelled baselines, and the three current views are added. Figma Starter quota prevented the final telemetry caption re-export; the documented flow, source and independent draw.io companion remain available. No Azure enablement or GitLab credential change occurred.

## PR #21 merged; local proof started - 1 November 2026

The user explicitly authorized merging PR #21. The verified head f59c9a48a73191c2efaec6f4976b6382b2e8407d passed CI and merged as dec89a84160bea68cd1f5d0a37aa54f4aaad95b3. The AKS/APIM design and official-icon diagram are now on main. See evidence/pr21-merge.json and [the local proof plan](docs/local-backend-proof-plan.md).

Current runtime evidence still covers the prototype and in-memory tests, not completed backend ingestion. Next: P1.1 application/contract/dependency review, then a bounded real Collector/Jaeger run. Cloud sizing, Terraform platform, Managed and live-model gates remain pending. Azure deployment stays disabled; GitLab/global Git credentials remain intact.

## Local review completed - 1 November 2026

P1.1 reviewed the policy/retrieval contracts, deterministic adapter, bounds, capture policy and locked versions. The current baseline passed 18 tests with one known TestClient deprecation; the CI input gap is already resolved. See evidence/local-workload-review.md and evidence/local-review-baseline.json. This proves local HTTP/in-memory assertions only.

Next: replace the deprecated test transport with the existing loopback fixture and validate a separate native Windows Collector/Jaeger profile. Real backend retrieval, exported-data canaries and owned-process lifecycle remain to prove. AKS/APIM, Azure spending, Managed and live models remain pending; Azure deployment stays disabled.

## Contracts and native preparation - 1 November 2026

The deprecated TestClient test now uses the existing real Uvicorn/HTTPX fixture. All 18 workload tests pass without warnings, including both OpenAPI schemas, real tool HTTP, typed outcomes, exact in-memory span edges and metadata checks. Native loopback-only Collector/Jaeger configurations pass their actual pinned validators. See evidence/local-workload-correction.json and docs/local-backend-runbook.md.

The first real backend attempt retrieved healthy/fault traces and passed canary checks, then failed a restart assertion because an expected 404 was not classified as absence. That failed attempt is retained in evidence/local-proof-attempt-1.json; a corrected rerun is pending before full acceptance. The runner owns its processes, captures and cleanup. Cloud, Managed and live models remain unproved and Azure disabled.

## Local backend boundary accepted - 1 November 2026

The corrected one-shot proof passed after the first restart-404 assertion failure; both attempts are retained. P1.4/P1.5/P1.6 can be assessed from exported/backend data and owned-process lifecycle, independently of cloud scope. Next: publish the workload/config/runner review PRs and verify hosted CI. The new configuration-checker source invalidates its earlier main-CI receipt until review/merge/revalidation; the tracker exposes that dependency rather than assuming new code ran on main. Azure deployment remains false, GitLab/global settings unchanged, and all local services are stopped.

## Historical local proof publication - 1 November 2026 (now merged)

Workloads PR #11, observability-config PR #5 and lab PR #23 contain the test correction, native profiles and reproducible runner/evidence respectively. See evidence/local-proof-publication.json. Source review found no confirmed secrets; reviewed matches are source-file SHA256 receipts. At publication those follow-ups remained open; their later approved merges are recorded below.

All six P1 steps have local acceptance evidence. The tracker is 15/41 because P2.8 needs revalidation of the changed configuration checker on main, and P2.9 depends on that receipt. Hosted branch checks are tracked on the PRs separately. Next: review/merge follow-up changes, verify main CI, then complete multi-repository release pinning. No cloud gate is accepted. Azure deployment remains false; global Git settings match the preservation baseline and GitLab credentials were not changed. All owned local listeners are stopped.

## Local-proof PRs merged; release preparation - 1 November 2026

The user-authorized workloads #11, observability-config #5 and lab #23 merges are verified at their CI-passing heads. Exact merge commits are in evidence/local-proof-main-merges.json. Local code/configuration and evidence now share a main-branch baseline. Four main CI runs are being checked, including a fresh read-only infrastructure CI dispatch. No Terraform deployment was dispatched.

Next: restore CI receipts from passing exact-main results, then follow docs/release-pinning-plan.md to create a source-pinned candidate manifest and validation. The workload registry digest remains unknown; no image publication, release tag, Azure resource or rollout is implied. Azure deployment stays disabled, and GitLab/global Git credentials remain intact.

## Exact-main CI revalidated - 1 November 2026

Fresh CI passed for all four exact main commits, including a read-only infra dispatch. Workload clean-checkout tests/container build, config source/Compose/Collector validation, lab checks, and infra backend-disabled Terraform/safety/mocked tests are evidenced in evidence/main-ci-revalidation.json. The deployment flag is false and both Azure GitHub environments remain reviewer-protected/main-only with administrator bypass disabled. No deployment workflow or Azure login ran.

P2.8/P2.9 can be reaccepted from these results and the retained disabled-preflight proof; P2.3 now has the required clean-checkout CI/build evidence after local P1 acceptance. Next: prepare the source-pinned candidate and fail-closed image-readiness validation. The application OCI digest is still unknown, and P2.4 is not complete. GitLab credentials/global Git settings remain intact.

## Source-pinned candidate prepared - 1 November 2026

releases/local-v0.1.0-source-candidate.json freezes the four tested commits, main CI IDs, existing Docker base/backend digest references, two native package checksums and 18 selected Git-object hashes. The offline validator checked source/receipt consistency and rejected deployable readiness as expected. All 28 local tests pass (20 tracker/sync and 8 release-candidate checks). See releases/README.md and evidence/release-pinning-validation.json.

The candidate has no workload registry digest and cannot pass --require-deployable. Existing image digests have not been newly pulled/resolved in this step. The manifest lives in its containing commit while its lab execution pin stays on the tested merged runner baseline. Current CI permissions/workflows are unchanged. Next: review the candidate, then select/review a registry publication and immutable container-replay path. P2.4 stays in progress; Azure/cloud, Managed and live-model gates remain pending. GitLab credentials and global Git settings remain unchanged.

## Historical release candidate publication - 1 November 2026 (now merged)

[Lab PR #24](https://github.com/AI-SRE-Oberveability/ai-observability-lab/pull/24) contains the candidate, validator/tests, exact-main CI receipts and merge receipts. See evidence/release-candidate-publication.json. The shared Project is at 18/41 accepted deliverables, with P2.4 in progress and no stale CI receipt. The candidate is not deployable: the workload image remains unpublished/unpinned, and the immutable container replay is pending.

The three requested PRs and preparation PR #24 are now merged; the delegated current-state receipt identifies lab main 7723a733b67e1992e3eb7a37e148e85be9321406. The publication receipt above describes the earlier review state. Azure deployment is still false; no registry publication, release tag, Azure authentication or resource operation took place. Global Git settings match the preservation baseline and GitLab credentials were not changed.

## Linux Compose implementation step — 8 November 2026

The delegated Ubuntu x86-64 proof is local, uncommitted work. A standard-library lab runner and six negative/synthetic acceptance tests now exist; initial red and green receipts remain private under the Linux runtime directory. No application, dependency, infrastructure or shared monitoring source changed. The existing policy -> real HTTP retrieval and OTLP HTTP Collector -> OTLP gRPC Jaeger architecture is preserved.

The first Docker API attempt failed with permission denied on the existing rootless socket from this restricted execution session. Matching UID/socket ownership does not establish API access. No Docker permissions, rootful service, credentials or global settings were changed. Pull/build/runtime ingestion remains unverified. Next: strengthen isolation/lifecycle checks, execute the runner, record available validation and preserve any failed attempts. New source requires new CI after parent review/publication; historical CI is not acceptance for these edits. G2/G3/G4/G5 and unpublished workload digest remain pending; Azure stays disabled.

## Linux validation boundary — 8 November 2026

The new standard-library runner assembles the existing four-service Compose profile with a unique owned project/network, private proof-only bounded Collector exports, explicit rootless backend UID mapping, read-only filesystems, nonroot workload users and existing resource/log/privilege bounds. It checks healthy/fault/external-W3C seven-span graphs, exact parent IDs and service/resource identity, typed 503 fault statuses, null usage and controlled question/baggage/key/document/answer canaries on specified surfaces. These are implemented assertions, **not observed Linux runtime results**. No application or shared monitoring source changed.

38 standard-library lab tests pass, including ten new Linux checks. Ruff lint/format, shared configuration source checks, real Docker Compose rendering of both source assembly and private proof configuration, and whitespace checks pass. Collector processors remain byte-structure-equivalent after private exporter injection; the private Jaeger memory cap is 1000 traces. The real engine API is denied by this execution sandbox; no images were pulled/built, no containers were started and no Linux ingestion, W3C/privacy/lifecycle result was observed. Failed permission, runner and test attempts are retained privately; sanitized evidence is in evidence/linux-compose-proof.json.

The Project sync script failed to obtain an authenticated token from its existing credential context; no credentials were changed and no success is claimed. Parent publication must perform sync after reviewing/publishing evidence. Historical source/evidence hashes are stale on this Linux checkout (including line-ending differences, old lowercase infrastructure paths and Windows provider-cache evidence); the generated tracker exposes revalidation instead of restoring acceptance. The offline release source check also fails at its lowercase infrastructure path; deployability rejects the missing workload digest as expected. No duplicate infrastructure clone or historical hash rewrite was created. Gitleaks reports eight reviewed SHA256 false positives, not a clean exit; no suppression was added.

Next: parent independently review the uncommitted diff, execute the runner with the existing rootless socket available, preserve all attempts, and accept only actual exported/queried backend evidence after validation. Then publish reviewed changes and collect new CI/sync receipts. Remaining: Linux runtime proof, source-watch portability/evidence revalidation, P2.4 published workload digest and immutable-registry replay, G2/G3 cloud targets/costed scope, G4 Managed, G5 live models and later P5/P6 experiments. No commits, pushes or Azure operations occurred in this delegation.

## Linux query regression — 8 November 2026

Host access is functional; earlier sandbox/socket and keyring failures remain historical. Parent attempts 796b761a33534f8d91a8f60e458ee881 and b06d8ab3983e473ab6ab00a309341dce reached healthy ingestion but failed fault validation on Jaeger 2.22's translated `http.status_code` integer 503. A sanitized query-shape regression failed before correction and all 11 Linux tests pass after query-only normalization. Every present legacy/modern status must be integer 503, including duplicate tags; typed errors, parents and identity checks remain. Collector allowlists and sibling sources are unchanged. Queries now persist privately before assertions. Next: real full runtime proof; CI/publication, registry replay and cloud/model gates remain pending. Project apply is deferred because the script hardcodes main evidence links for branch-only files; safe dry-run only per scoped instruction.

Runtime attempt 3fb5629601434e8d8fb20814635411d7 passed all three graphs and actual container controls, then rejected SDK numeric metric exemplars. Private file exports show only numeric/time/trace/span correlation with no filtered labels; the telemetry contract forbids trace labels, not exemplar correlation. A narrow real-shape regression failed then passed (12 Linux checks). Query/export allowlists stay strict: exemplars now permit only typed numeric/time/hex-ID fields and empty filtered attributes. Full canary checks still cover the serialized exports. No sibling changes. Cleanup passed; next replay must establish privacy and restart as well.

## Linux runtime proof completed — 8 November 2026

Final run d3f35910e0074a6db6423c6eac0daf95 passes against the final runner bytes after import ordering cleanup; f3c56e268d204d3ebbc31ecf840b825b also passed before that formatting-only change. Real healthy/fault/external-W3C seven-span graphs, typed errors/exact 503, identity/parents, Collector raw trace/metric exports, six canary surfaces, bounded two-attempt fault, actual loopback/hardening/resource checks and ephemeral restart all passed. Owned containers/networks/volumes are absent and ports released. Raw queries are retained privately before assertions. No application/config/infra sibling source changed.

40 lab tests (12 Linux checks), lint/format and config/Compose checks pass locally. Gitleaks default detector exits 1 for eight independently corroborated source/icon SHA256 receipts, including historical CRLF contract bytes; no suppression or detector exit-0 claim. Fresh P1.4/P1.5/P1.6 acceptance is recorded with exact watched-source hashes in evidence/linux-compose-proof.json; tracker dependencies remain in progress because historical upstream source receipts are stale, rather than reaccepting unrelated Windows receipts. Earlier sandbox failures, both parent 503 failures and the new exemplar assertion failure remain history.

Next: parent independently review/rerun/commit/push, then run Project apply after evidence exists on the linked ref and collect branch/main CI as appropriate. Safe Project dry-run succeeds; existing auth is functional and earlier auth denial is historical. No branch-ref switch exists; no live Project updates or issue closures occurred. Remaining: historical source-watch portability/dependency review, P2.4 published OCI digest/immutable replay, new hosted CI and pending G2/G3/G4/G5. No commits, pushes, Azure operations, deployment gate changes or paid inference.

## Independent Linux review corrections — 8 November 2026

Current architecture is unchanged. Seven focused review regressions were run RED before implementation (12 failures, three missing-helper errors); all seven now pass locally. Owned command sessions receive bounded TERM/KILL and diagnostics; cleanup retries always inspect project-labelled containers/networks/volumes. Backend queries bind exactly one trace to the requested ID; successful graphs require observed 200/status/outcome/bounds. Scope attributes are rejected and the dedicated question marker is scanned independently. Export acceptance reconciles exact cohort span identities/names/service multiplicity and both-service operation metrics. Producers stop before bounded completion polling; Collector stops before final logs/file privacy scanning. Private retrieval health readiness uses its existing 8080 network endpoint. Existing 503 normalization and strict numeric exemplar checks remain.

These are local test results; current bytes still require actual Docker replay. RED/GREEN receipts are private in runtime/review-fixes. Historical successful runtime remains retained. Project live sync is explicitly deferred because feature-only evidence URLs would target main; only safe dry-run is authorized for this step. Next: full suite/lint/format and actual final-byte Docker proof. Remaining: final runtime acceptance, parent publication/new CI, historical receipt portability, missing P2.4 registry digest and unchanged cloud/model gates. No commits/pushes or sibling changes.

Review-fix validation continuation: full standard-library lab suite now passes 50 tests (22 Linux checks, including ten independent-review regressions), with Ruff lint/format passing. Review replay 8922096527344649b438daf94f2a1332 passed before the final orchestration/import refinements. Replay cab03ed4064d4b21b9966a61811f4f76 then failed Compose startup because 127.0.0.1:16686 became allocated after preflight; all three owned-resource inspections were empty on each cleanup attempt, but port release verification failed. This failure remains historical; no unrelated resource was stopped. Cleanup diagnostics now distinguish owned resources from occupied ports. One additional RED/GREEN regression rejects unexpected HTTP codes even on internal healthy spans. A final-byte replay is running; no new backend acceptance is inferred yet. Live Project sync stays deferred for main-only evidence URLs; safe dry-run only. Architecture/gates and remaining publication/registry/cloud work are unchanged.

## Independent-review final runtime accepted locally — 8 November 2026

Final runner SHA256 `b8471632d82d38bedde164191c26329df772146f01acc12d92e82aed4f14f81f` matches actual passing replay `93617e4df9244ea991aaa5f450130e43`. Healthy/fault/W3C graphs passed with requested backend cohort binding; fault completed in 0.039 seconds with two calls. Frozen Collector exports reconcile exactly 21 cohort spans and calls/duration data points from both services. All six final surfaces passed independent marker/full-question/key/baggage/all-document/generated-answer scans, scope/metadata allowlists and preserved strict numeric exemplar checks. Private retrieval readiness, actual container bounds, ephemeral restart and owned cleanup passed; down errors zero, labelled containers/networks/volumes absent and expected ports released. Earlier review success and startup port collision remain in evidence history.

50 stdlib lab tests pass on Python 3.12.16 and 3.14.9; Ruff lint/format pass. RED/GREEN receipts remain private under review-fixes. SIGTERM/Ctrl-C route through owned cleanup; SIGKILL/host failure cannot be caught, and orphan descendant reaping belongs to Linux init after owned group termination. Local images/private receipts remain intentionally retained. No log pipeline, universal PII, P6 load or Managed claim is made.

Parent receipts separately establish backend-disabled infrastructure validation and unchanged-source feature publication at `62f079f9c9a25e0c83f202931bd30bca18959a3a`; supplied branch CI run `42433363253` passed without a deployment workflow. These do not refresh lab/main CI or historical Windows/CRLF/case-path receipts. No sibling source, Azure/gate, global Git/auth, Docker privilege/service or unrelated resource was changed. No commits, pushes or merges occurred. Project safe dry-run passes; live sync is explicitly deferred to parent publication because existing links hardcode main. Next: parent review/publication and correct-ref synchronization/new CI. Remaining: stale historical dependencies/portability, P2.4 missing OCI registry digest/immutable replay and unchanged G2/G3/G4/G5 gates.

Final envelope-edge follow-up: an empty metrics envelope alongside valid records reproduced one additional RED failure; per-envelope nonemptiness now rejects it. Eleven review regressions and 51 total lab tests (23 Linux) pass on Python 3.12/3.14, with lint/format passing. Final replay **83a8ef9c5e674ec3b347564e9287e3a3** passed on runner SHA256 `90a86804488a032fdfab938bb7ebbffa532c6625728cc5ce1912a6c0e944e9cf`; this supersedes 93617e4df9244ea991aaa5f450130e43 for current-byte acceptance. All three graphs, exact 21 exported spans, both-service operation metrics, frozen privacy surfaces, readiness/restart and owned cleanup passed. Previous successes/failures remain history. Architecture and outstanding publication/CI, deferred main-link Project sync, registry digest and cloud/model gates are unchanged.

## Parent verification and final review — 8 November 2026

A second independent code review approved final runner SHA256 `90a86804488a032fdfab938bb7ebbffa532c6625728cc5ce1912a6c0e944e9cf` with no remaining blocking security or logic findings. The parent independently reran those exact bytes as `9adff0b94c5d413f8dead5073dda5912`: healthy, controlled dependency 503 and external-W3C cohorts each produced seven expected spans, with exact exported reconciliation of 21 spans, both-service operation metrics, frozen six-surface canary checks, restart and owned cleanup passing. The dependency fault completed in 0.0469 seconds with two calls. See evidence/linux-parent-verification.json; raw captures remain private.

Final Python 3.12 verification passed 51 lab tests with and without site packages, 18 workload HTTP/contract/telemetry tests, 11 infrastructure safety tests and two mocked Terraform tests. Lint/format/source/Compose checks and backend-disabled, locked Terraform initialization/validation passed. The default Gitleaks detector still exits 1 for eight independently corroborated source/icon digest receipts; no credential finding or suppression was introduced. Existing source-watch invalidation remains explicit rather than restoring unrelated historical acceptance. Only lab source changed; the requested infrastructure feature branch is published unchanged and its read-only CI passed. Feature publication and lab branch CI are the next step; no main merge, Azure operation, registry publication or paid inference is authorized. Live Project apply remains deferred until evidence can be linked to the correct ref.

## Feature source published — 8 November 2026

Validated code commit `a8419510d7c74b2211e255ee50639e50d2717da9` is pushed to `feature/ai-sre-platform-lab` in ai-observability-lab; exact remote SHA readback matched. Hosted branch CI `42435140058` succeeded on that exact commit. Draft review PR #25 is open against main and remains unmerged. The requested infrastructure feature branch is published unchanged at `62f079f9c9a25e0c83f202931bd30bca18959a3a`, with passing read-only branch CI `42433363253`. Workload/config clones remain clean on their existing main commits. All four remote main heads are unchanged and AZURE_DEPLOYMENT_ENABLED remains false.

See evidence/linux-feature-publication.json for source/CI/PR receipts. This documentation receipt is a descendant of the validated code commit; it does not change runner bytes or claim a main merge, registry digest/replay, new cloud acceptance or paid inference. The HLD and generated tracker retain historical-source revalidation explicitly. Project dry-run passes, but live synchronization remains deferred: the helper has no branch-ref option and would link new feature-only evidence to main. Next recommended work is Linux-portable historical evidence/release-path revalidation and correct-ref Project linking, followed by reviewed immutable workload-image publication/replay. Cloud/model gates remain pending.
