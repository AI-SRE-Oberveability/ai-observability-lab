# Architecture and ownership

The current proposed target is documented in [AKS, Citadel/APIM governance and observability architecture](architecture/README.md), with editable [FigJam diagrams](https://www.figma.com/board/JxOlJjtrEmIFrhRU8ltID0), Mermaid sources and stable previews. [HLD.md](../HLD.md) distinguishes verified work from planned cloud components.

| Repository | Sole ownership |
| --- | --- |
| AI-SRE-Oberveability/AI-Observability-Infra | Terraform, new Azure resources, bootstrap/state, scoped identities and cost controls |
| AI-SRE-Oberveability/ai-agent-workloads | Agent/tool contracts, synthetic fixtures, images and app Helm/manifests |
| AI-SRE-Oberveability/ai-observability-config | Shared Collector/backends, instrumentation/vendor config and monitoring profiles |
| AI-SRE-Oberveability/ai-observability-lab | HLD/diagrams, release coordination, tracker, experiments and evidence |

Four independent repositories share a parent workspace, not a containing Git repository. GitLab credentials and unrelated repositories remain untouched.

Current proof covers local prototype tests, image builds, config/Terraform validation and four main CI pipelines. Azure execution remains disabled. AKS/platform deployment, real backend trace proof, image registry publication, Managed compatibility and live models remain later work.

Optional existing personal Azure AI resources are candidates only, pending ownership, region, endpoint/SDK, quota, network, identity and cost validation. No automatic migration/import or customer-resource reuse is authorized by the diagram.

Citadel/APIM is selected for the planned model-access path. See the [step-by-step governance plan](architecture/governance-plan.md). AKS pods use gateway-scoped identity; APIM has separate model access. Terraform owns gateway resources/policies. The prior diagram baseline is retained; implementation and cloud/live-model gates remain open.

[Open the editable draw.io companion with official Azure icons](architecture/azure-governance.drawio); [view the SVG](architecture/azure-governance.svg). It embeds six unchanged Microsoft Azure product icons and retains editable labels, connectors and containers.
