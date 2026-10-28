# High-level design — current, target and remaining work

Version: 0.5 organization migration authorized. Updated: 29 October 2026, Asia/Dubai. Execution: **organization and four transfers verified; shared Project setup in progress**.

## Purpose

Provide three synthetic use cases: a policy assistant, a service-status agent and a read-only SRE copilot. Observe AI workload behavior separately from using AI to investigate monitoring evidence. Use personal Azure/GitHub targets; preserve Dynatrace Managed as the preferred later compatibility profile.

Confirmed implementation choices: **Terraform owns Azure infrastructure**, Helm/Kubernetes manifests own workload/observability deployments, and four repositories under `AI-SRE-Oberveability` separate resource ownership. The organization is owned by the personal account `javedkumail`. All four transferred repositories retain their IDs, published commits and public visibility. The infrastructure destination is `AI-Observability-Infra`; other names match the source folders. Reviewed source is published to all four repositories; initial commit receipts are recorded below. GitLab credentials remain intact. Engineering standards are defined in `docs/engineering-standards.md`.

## Current local draft

```mermaid
flowchart LR
  T[Synthetic caller] -->|Lab authentication| A[Draft Python agent API]
  A --> P[Deterministic model adapter]
  A -->|HTTP and W3C context| R[Draft retrieval tool]
  R --> D[Invented policy documents]
  A -.->|Planned OTLP export| C[Collector configuration validated]
  R -.->|Planned OTLP export| C
  C -.->|End-to-end validation pending| J[Jaeger]
```

Solid arrows describe the local service behavior exercised in the earlier 18-test run. Dashed arrows remain unproven as a complete running backend path. Existing in-memory trace assertions do not establish Jaeger ingestion. Collector and Jaeger binaries are present; local lifecycle coordination still needs work. The draft CI has an unresolved dependency-lock input. No live model, Azure or Managed deployment is present.

## Proposed personal Azure target

```mermaid
flowchart TB
  O[AI-SRE-Oberveability organization] --> G[Four public GitHub repositories]
  O --> P[Shared GitHub Project]
  P --> T[POC tasks and evidence]
  G --> W[Scoped GitHub Actions workflows]
  W --> F[Terraform plan and authorized apply]
  F -->|OIDC and scoped RBAC| Z[Dedicated personal Azure lab scope]
  W -->|Runner with verified connectivity| K[AKS workloads]
  Z --> K
  U[Authenticated synthetic caller] --> A[Policy or status agent on AKS]
  K --- A
  A --> R[Allowlisted retrieval and status tools]
  A --> M[Mock or approved Azure model]
  A -->|Selected SDK signals| C[OTel Collector]
  R -->|Selected SDK signals| C
  C -->|Verified supported endpoints| B[Chosen telemetry backend]
  N[OneAgent and compatible Operator] -->|Native supported path| D[Licensed Managed backend on supported hosts]
  K --- N
  B -.->|Managed profile after validation| D
```

This diagram is a proposed target, not deployment proof. Infra owns Azure, state, identity and budgets; workloads owns applications/images/deployments; observability-config owns shared telemetry/monitoring; lab owns coordination/evidence. A release manifest pins their tested versions. The OneAgent native path stays independent of the arbitrary Collector. Separate experiments compare instrumentation modes and duplication.

Azure choices remain open: exact subscription/tenant, region, node sizes, public/private connectivity, reachable CI runner, model/quota, retention and active/idle cost. A costed plan precedes cloud spending. Managed choices additionally require entitlement, approved host/storage sizing and version compatibility.

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

**What we are going to do next:** finish the shared GitHub Project and task mapping, then publish its verified URL. Organization creation, ownership verification and all four repository transfers are complete. The next application implementation package remains local vertical-slice/backend validation.

**What remains:** backend ingestion/lifecycle evidence; repository/CI completion; personal targets and budget; costed Azure IaC/deployment; Managed entitlement and compatibility; status agent; SRE adapter/copilot; live-provider and comparison experiments; demo, rebuild and teardown.

After every work step the tracker supplies current status, next executable work and remaining decisions. Update this HLD whenever a component, boundary, ownership rule or telemetry path changes.

<!-- publication-progress -->

## Verified source publication

| Repository | Initial reviewed commit | Status |
| --- | --- | --- |
| ai-observability-infra | `b21c746acac6` | Pushed and verified |
| ai-agent-workloads | `6fc332a2cddf` | Pushed and verified |
| ai-observability-config | `9d81a64e0fea` | Pushed and verified |
| ai-observability-lab | `0d5cf9f01db8` | Pushed and verified |

The lab receipt pins the initial reviewed source commit; later coordination updates are descendants. Source publication does not establish a running backend, active CI, Terraform deployment or Managed compatibility. Component ownership is unchanged.

## Organization migration status

`AI-SRE-Oberveability` is created on GitHub Free, and authenticated membership verifies javedkumail as active owner. 4/4 repositories have transferred with IDs, commits and public visibility preserved. The shared GitHub Project is pending. GitLab credentials and global Git helpers remain unchanged.

| Repository | Actual owner | Transfer verification |
| --- | --- | --- |
| AI-Observability-Infra | AI-SRE-Oberveability | transferred_and_verified |
| ai-agent-workloads | AI-SRE-Oberveability | transferred_and_verified |
| ai-observability-config | AI-SRE-Oberveability | transferred_and_verified |
| ai-observability-lab | AI-SRE-Oberveability | transferred_and_verified |

Organization grouping changes repository ownership and future OIDC inputs, not component responsibilities. Verify the actual new owner/repository OIDC subject before configuring Azure federation. No Azure federation was deployed before this move.

## Project setup continuation — 29 October 2026

The shared Project remains uncreated in the local mapping. Chrome browser control is disconnected, so Project creation is not claimed. Repository mapping, documentation and transfer evidence can be published independently. Existing GitHub repository authentication remains available; no GitLab credential/global helper changes are needed.
