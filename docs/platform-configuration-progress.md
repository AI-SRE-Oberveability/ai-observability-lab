# P2.13 dependency and configuration implementation

PR #36 is merged with passing exact-main CI. The approved plan's first input/configuration slice is implemented on review branches; the overall P2.13 task remains in progress.

- [Config PR #1](https://github.com/AI-SRE-Oberveability/ai-platform-config/pull/1): immutable CRD/schema/licence inputs, hash-locked Python/Kustomize, three profile builds and 32 owned objects. Twenty tests and Linux/Windows CI pass, including rendered-CRD equality to locked upstream objects. No RoleBinding, application ServiceAccount/Deployment or controller is created.
- [Charts PR #6](https://github.com/AI-SRE-Oberveability/ai-observability-config/pull/6): real Argo chart lock plus archive/private Helm hashes. Default renders zero objects; explicit smoke renders 56 without Namespace/CRD emission. It is not a deployable controller profile. The first lint failure is retained and corrected CI passes.
- [Lab PR #37](https://github.com/AI-SRE-Oberveability/ai-observability-lab/pull/37): HLD/tracker, actual source bindings, attempts, CI and preservation receipts.

Argo 3.6.1 / chart 10.18.0 use upstream-matched private Helm 4.3.1 and Kustomize 5.8.3. Global Helm remains 3.19.0. Kubernetes 1.35.0 is an offline API/schema baseline only; no actual AKS version/target is verified or approved. The matrix pins real published review commits; no GitOps catalog or workload chart revision is invented.

The configuration includes four Namespaces, two quotas, two LimitRanges, two unbound read-only Roles, nineteen NetworkPolicies and three original Argo CRDs. Source/schema/policy checks do not prove live admission/CEL, pod-security/network enforcement, controller connectivity or backend ingestion. APIM egress remains closed pending the exact target/identity/network contract.

All seven repo IDs/origins, original remote/global Git settings, seven existing telemetry/profile hashes, two unseeded repositories and disabled Azure flags were verified. GitLab credential stores were not changed or exported. No Azure/Kubernetes apply, Argo sync, registry publication or global tool upgrade ran.

Next: review/merge these concrete PRs, then complete platform/application chart profiles, GitOps environment pins and bootstrap/combined ownership checks. P2.14 seven-repo CI, P2.15 rename/Project cutover and P2.16 fresh canonical runtime/source baseline remain later work. Watched workflow changes invalidate prior exact-main CI receipts until approved merge/revalidation; branch CI is recorded separately. Historical backend and release evidence remain unchanged.
