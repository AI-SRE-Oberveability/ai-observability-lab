# Citadel/APIM governance implementation plan

Updated 1 November 2026, Asia/Dubai. The user selected Citadel/APIM for the target architecture and step-by-step plan. This authorizes design/documentation; Azure execution remains disabled. No gateway, AKS cluster, identity or live model has been deployed by this change.

## Target and ownership

Custom policy, status and SRE agents run on AKS. Their approved live model calls use APIM outside the cluster, then an allowlisted new or verified existing Foundry/OpenAI deployment. The local and first AKS mock cohorts remain deterministic. Optional existing resources stay unverified candidates; no discovery, adoption, import or deletion is implied.

Citadel supplies the governance pattern. Terraform owns selected Azure resources and versioned APIM XML policies. This is a scoped implementation, not a claim that the entire upstream accelerator, notebooks, usage data platform or hosted-agent stack is installed. APIM SKU/region, network mode, API/schema, model and provider versions remain costed design decisions. API Center, Redis, Cosmos/Event Hub/Logic Apps analytics, multi-region failover and paid safety services are optional extensions with separate justification.

| Repository | Responsibility |
| --- | --- |
| AI-Observability-Infra | Terraform bootstrap/platform/APIM modules; backend/access inventory and XML policy fragments; APIM managed identity, roles, DNS/networking, diagnostics and lifecycle |
| ai-agent-workloads | Agent-to-gateway adapter, validated API contract, per-service identity configuration, time/retry/output bounds and typed policy errors; application Helm/manifests |
| ai-observability-config | Collector allowlist, gateway diagnostic capture rules, correlation queries, dashboards and bounded monitoring read profiles; no gateway resource ownership |
| ai-observability-lab | HLD/diagrams, phased plan, release manifest, controlled governance scenarios and sanitized evidence; shared tracker/Project |

Infra consumes reviewed diagnostic requirements from observability-config; Terraform remains the single writer for APIM diagnostics and policies. Pinned cross-repository releases make that contract reproducible.

## Three identity boundaries

1. GitHub OIDC: separately scoped plan/apply and release runner identities; protected environments and reachable runner routes.
2. AKS Workload ID: a Kubernetes ServiceAccount/federated identity per agent obtains a token for the gateway API audience. APIM validates issuer, audience, calling identity and allowed roles/claims. Use-case attribution comes from validated identity, not a caller-controlled header.
3. APIM managed identity: APIM obtains the appropriate backend token and uses only the model resource roles required by the selected API. AKS agents receive no direct model-inference role in the governed cohort. Strip/overwrite caller authentication and backend-routing headers before forwarding.

Authentication does not establish connectivity. Select and prove AKS-to-APIM, APIM-to-model and runner-to-platform DNS/TLS/routes together. Restrict backend access to the supported gateway route/identity and test attempts to bypass it. Do not represent a Kubernetes NetworkPolicy alone as a complete Azure service firewall.

## Step-by-step execution plan

| Step / tracker mapping | Work | Exit evidence |
| --- | --- | --- |
| 1. Local baseline - P1.1-P1.6 | Review contracts, run deterministic policy/tool services, Collector and Jaeger; exercise one bounded failure | Repeatable start/stop; backend-retrieved trace graph and exported-data canary checks |
| 2. Costed design - P3.1/P3.2 | Confirm G2 personal targets, region/budget; assess only named reuse candidates; select minimum AKS/APIM footprint, routes, retention and identities | Dated active/idle costs, ownership and compatibility matrix; no Azure execution |
| 3. Terraform foundation - P3.3 | Define protected state/bootstrap, exact OIDC subjects, scoped roles and AKS/ACR/Key Vault/networking | Provider/module locks, formatting/validation/security checks, reviewed bootstrap and runner access |
| 4. Governance IaC - P3.7 | Define APIM, APIs/backends, managed identity, access mapping, policies and metadata diagnostics; verify AzureRM support and isolate any required AzAPI resources with one state owner | Offline policy/contract checks, provider coverage, complete backend inventory, denied routes and concrete costed plan; no apply |
| 5. Concrete review - P3.4 | Review combined platform/gateway plan, cost, privileges and exact lifecycle; obtain G3 authorization | Reviewed source/state/values fingerprint and explicit scope; deployment flag stays false until a later authorized enablement |
| 6. Mock AKS release - P3.5/P5.5 | After approved enablement, provision through guarded Actions, publish immutable images and deploy Helm; keep deterministic mode; validate adapter against synthetic gateway responses | Deployment/smoke/identity checks, contract/error tests and mock-mode privacy proof; no live usage claim |
| 7. Governed live cohort - P5.5/P6.6 | After G5, enable only approved model/backend and bounded use-case quotas; validate telemetry with observability-config | Real allow/deny and usage-limit results, bounded faults, backend trace/query evidence and no prohibited content |
| 8. Compare and clean up - P6.6/P3.6/P6.5 | Measure governance overhead and failure behavior; rebuild from pinned sources; perform reviewed scoped cleanup | Versioned outcomes, unknowns, residual-charge inventory; reused resources excluded |

G4 remains separate for licensed Managed; baseline governance evidence need not wait for Managed. Native OneAgent ingestion remains independent of custom Collector routing. Foundry-hosted agents, MCP/A2A publishing and additional safety policies remain later scoped comparisons.

## Gateway contract and acceptance cases

The following are required evidence cases, not implemented or passing controls today:

- Authorized use-case/model succeeds; missing/expired/wrong-audience token and unauthorized use-case/model fail. Reject spoofed identity, model-routing and quota-key headers.
- Check per-use-case request and token rates/quotas against the selected tier, API schema and policy version. Test token-rate 429 and token-quota 403 distinctly from authentication/authorization failures; capture actual supported retry/reset semantics. Limits can be estimated or distributed and are not a guaranteed billing cutoff.
- Bound connection/response/stream time, attempts, backoff, tool loops and output size. Respect a supported Retry-After only within the total deadline; fail closed on identity/policy errors. Do not silently fail over to a direct model endpoint. Streaming cancellation/usage and any unsupported policy combination get explicit results.
- Disable prompt/completion, document, tool-argument, authorization-header and subscription-key logging at every diagnostic/export surface. Use synthetic canaries to inspect gateway, application and backend-observed signals. PII/safety filtering does not substitute for this capture policy or application tool controls.
- Validate W3C propagation or explicitly record correlation gaps. Join bounded application/gateway/backend request IDs with controlled service/version/use-case/model identity. Measure missing/duplicate spans, policy outcome, latency, throttles and available usage; keep unique request/user identifiers out of metric labels.
- Governed agents cannot call models directly. Test gateway outage, model timeout/429/5xx and denied-egress cases. A direct-model comparison, if authorized, uses an isolated comparison identity and never leaves bypass access on governed agents.
- APIM diagnostics go to the selected Azure Monitor path; no automatic APIM-to-Collector export is assumed. A future SRE adapter receives separately scoped, bounded query-only access to approved gateway summaries. No policy write, Kubernetes/Azure command or automatic remediation is added.
- Terraform creates/destroys only dedicated owned resources; inventory all backend registrations before changes. Retained evidence/state and externally owned reuse references have explicit lifecycle decisions. Do not run sample azd purge/teardown against reused resources.

## References and validation boundary

- [Citadel lab](https://microsoftlearning.github.io/mslearn-ai-governance/lab/) and [prior fit review](citadel-governance-review.md): reference context. The workshop fork and Azure-Samples upstream are different source baselines; pin/review an exact commit before adopting code.
- [APIM AI authentication](https://learn.microsoft.com/en-us/azure/api-management/api-management-authenticate-authorize-ai-apis): client authorization and managed backend identity options.
- [LLM token-limit policy](https://learn.microsoft.com/en-us/azure/api-management/llm-token-limit-policy): supported schemas/tiers, 429 rate and 403 quota behavior and token estimates. Verify against the selected version.
- [AzureRM APIM API policy resource](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/api_management_api_policy): coverage starting point; complete module/provider compatibility review remains P3.7.

This design does not establish a cost estimate, enforced gateway control, trace continuity, Managed parity or live-model quality. Those claims require the specified runtime evidence. Next ready work remains P1.1. G2-G5 remain pending. GitLab credentials/global helpers and Azure deployment settings are unchanged.
