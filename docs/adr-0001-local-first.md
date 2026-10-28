# ADR 0001: local synthetic baseline before personal cloud provisioning

Date: 2026-10-28 (Asia/Dubai). Status: proposed; superseded as the execution baseline by `../POC_PLAN.md` and `../HLD.md`, pending user acceptance.

The provided brief is the project source of intent. The workspace already contains study files; the new `personal-ai-observability` directory isolates this lab. Four sibling source directories are prepared as future private repositories. No Git repository, remote or cloud resource is created until its personal owner is confirmed. The original brief remains at the parent level and is not intended for automatic publication.

The first application is a synthetic policy assistant. An explicit three-step workflow plans a tool choice, retrieves from an independent HTTP service and returns an extractive answer with invented document references. Its deterministic adapter is a test fixture, not an LLM. A versioned expected-answer dataset tests its small supported surface independently of transport success. Usage fields are null; mock timing cannot establish real model latency or cost.

Manual OTel instrumentation owns the initial spans. There is no OneAgent or automatic HTTP instrumentation in this profile. All application-to-tool requests propagate W3C trace context. An allowlist controls metadata; neither prompts nor retrieved passages enter telemetry. The SDK emits metrics with operation/outcome labels and operational JSON logs with trace correlation. Logs stay local in this first slice; OTLP log ingestion remains future work. The Collector receives traces and metrics, exports traces to Jaeger and exposes metrics in Prometheus format.

Use Compose where Docker is available. On Windows, pinned native Collector and Jaeger binaries are a proposed alternative; their downloads were verified but a complete backend run was not validated. Native endpoint overrides and lifecycle coordination remain to be implemented from the owned Collector configuration. Local services should bind to loopback. No machine-wide lab service or scheduled task was installed.

Dynatrace Managed remains the preferred later compatibility profile. Native local evidence establishes only the selected OTel path. It establishes no OneAgent enrichment, Managed feature support, AKS topology or reference enterprise environment parity. An authorized SaaS comparison is separate and optional. Managed installation waits for entitlement, supported sizing and an exact version matrix.

The future SRE assistant is separate from this policy assistant: bounded, read-only evidence ingestion, source references, uncertainty and human review. This slice adds no SRE or remediation tool. Public/customer accounts and prior customer artifacts are outside the implementation scope.

Consequences: basic tracing and failure behavior are testable without cloud spend. Cloud IaC, live providers, token budgets, Managed integration and SRE incident reasoning still need their own implementation and evidence. The native backend fallback does not replace the later AKS/Operator experiment.
