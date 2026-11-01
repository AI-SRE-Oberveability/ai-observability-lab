# Citadel governance lab: fit review

Reviewed: 1 November 2026, Asia/Dubai. Scope: documentation assessment; no deployment, notebook execution, Azure inventory or full source-code audit.

> Historical assessment: the user subsequently selected APIM for the target design. See [the current governance plan](governance-plan.md). This earlier review does not describe the latest selection.

## Recommendation

Use Citadel as a reference for an optional governed-model-access experiment after the local baseline is proved. This review does not select an APIM SKU, add committed cloud scope, accept an upstream implementation, or replace Terraform. The existing AKS proposal and three use cases remain the target under review in PR #21.

## What the references establish

The [Microsoft Learning lab](https://microsoftlearning.github.io/mslearn-ai-governance/lab/) describes an APIM governance hub with a Foundry workload spoke, deployed with azd/Bicep and scripts. Its exercises cover onboarding, access contracts, PII and usage telemetry, with optional hosted-agent/A2A/MCP exercises. The listed footprint includes StandardV2 APIM, two-region model capacity and supporting analytics services. This is a larger footprint than our resource-group foundation.

The lab directs learners to a [personal fork's workshop branch](https://github.com/mohamedsaif/ai-hub-gateway-solution-accelerator/tree/workshop). The [Azure-Samples upstream](https://github.com/Azure-Samples/ai-hub-gateway-solution-accelerator) currently advertises citadel-v1 and separates backend, access and preview publish contracts. Treat these as different source baselines; do not mix branch instructions. Pin and review an exact commit before adapting code.

## Proposed fit with our design

These are design recommendations for a future experiment, not verified behavior of our implementation.

| Existing boundary | Optional Citadel-inspired extension | Ownership |
| --- | --- | --- |
| Custom policy/status/SRE agents on AKS | Route approved live model calls through a governed APIM endpoint | Infra owns gateway resources; workloads own the client adapter |
| Optional existing personal Foundry/OpenAI backend | Register only explicitly verified endpoints and models | Infra manages an approved backend inventory |
| Per-service pod identity | Validate the selected client authentication and narrowly scoped gateway-to-model identity | Infra owns identities/roles; workloads consume configuration |
| Metadata-only OpenTelemetry and selected backend | Correlate gateway decisions with application traces; measure missing/duplicate spans | Observability-config owns capture rules, queries and dashboards |
| Read-only SRE adapter | Read bounded governance/usage summaries through an explicit adapter contract | Workloads; no policy mutation or remediation capability |

A gateway does not enforce all agent behavior. Keep tool allowlists, execution/time budgets, retrieval trust boundaries and read-only controls inside the application. Correlation across AKS, APIM and the model must be proved with exported and backend-retrieved evidence; enabling diagnostics alone is insufficient.

## Defaults and assumptions requiring adaptation

- Privacy: the lab enables LLM message logging. Preserve our metadata-only default and verify every gateway diagnostic/body-log surface with synthetic canaries.
- Networking: the lab includes portal-access shortcuts that broaden network access. Keep our reviewed networking design and solve runner/developer reachability explicitly.
- Reuse and lifecycle: the lab warns backend onboarding can replace registrations and hub cleanup excludes separately created spokes. Use a complete reviewed inventory; never apply sample teardown to reused resources.
- IaC: translate only the selected resource/policy subset into supported Terraform/AzAPI resources after checking provider coverage. Give each resource one state owner. Do not run a second azd/Bicep owner against Terraform-managed resources.
- Cost: estimate the exact region/SKU, active and idle charges, model quota and retention before adding the gateway. No cost estimate or spending cap is established by this review. Usage quotas and budget notifications must not be described as guaranteed billing cutoffs.
- Version/support: verify the exact gateway capabilities and Foundry API/SDK/model versions. Hosted agents, A2A/MCP and preview contracts are optional later comparisons. No Managed compatibility follows from Application Insights examples.

## Step-by-step adoption proposal

1. Complete P1.1-P1.6: reproducible local API/tool flow, bounded failure, metadata checks and a trace retrieved from Jaeger.
2. At P3.2, choose one explicit governance question, such as whether per-use-case throttling limits a synthetic caller. Compare a direct-model cohort with a gateway cohort under matched conditions.
3. Confirm G2: personal tenant/subscription, region, currency/budget and any candidate reuse resources. Inspect a pinned source baseline and select the smallest supported subset.
4. Present the costed Terraform changes, identity/network/state ownership, policy acceptance cases and scoped cleanup for G3. G5 additionally covers actual model/quota/live usage.
5. Only after those gates, implement infra modules and an endpoint adapter. Test authorized/denied calls, bounded 429 handling, policy bypass paths, actual available token usage, capture privacy and trace continuity. Record unsupported behavior and unknown usage explicitly.
6. Add advanced safety, failover, hosted-agent/A2A/MCP or usage-storage experiments only when separately useful and costed. Prove cleanup excludes reused resources.

## Current status and remaining decisions

CI is established across four repositories. AKS, the optional gateway, live Azure AI and Managed integration are not deployed. Accepted delivery count remains 11/38; this documentation review does not complete cloud-design or deployment tasks. P1.1 stays the next ready implementation step. G2-G5 remain pending, and PR #21 remains open for review.

The user authorized review of the linked material. No new cloud or gateway implementation approval is inferred. GitLab credentials, global Git configuration and existing remotes are unchanged.
