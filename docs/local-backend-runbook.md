# Windows local backend proof

Run from the personal-ai-observability parent workspace with Python 3.12 and the existing hash-locked workload environment. Do not use cloud credentials or live documents.

```powershell
# Fresh environment only:
py -3.12 -m venv ai-agent-workloads/.venv
ai-agent-workloads/.venv/Scripts/python.exe -m pip install --require-hashes -r ai-agent-workloads/requirements-dev.lock.txt

# Download/extract verified packages if absent:
python ai-observability-lab/scripts/install_local_backends.py

# One-shot start, traffic, export/backend assertions, stop and restart proof:
ai-agent-workloads/.venv/Scripts/python.exe ai-observability-lab/scripts/prove_local_backend.py
```

The runner verifies the downloaded archive hashes and compares each executable to its archive. It binds only loopback, refuses existing listeners, starts Jaeger and Collector, runs separate Uvicorn agent/retrieval servers, then stops only its own child processes/threads in finally blocks. It never changes Docker, credentials, Git configuration or Azure. Native Windows processes are not container-isolated; use this small synthetic cohort on the local machine only.

Ports: Jaeger OTLP gRPC 14317, query HTTP 16686 and gRPC 16685; Collector OTLP HTTP 14318, application metrics 18889 and internal metrics 18888; agent 18080 and retrieval 18081. Do not expose or forward these ports. Readiness and cleanup are bounded; a failing check exits nonzero rather than claiming completion. Abruptly killing the parent process can bypass finally cleanup; preserve its terminal until it finishes and investigate only its recorded owned PIDs if interrupted.

The deterministic model returns unknown/null token usage. A healthy request must produce the exact seven-span graph across two services; a synthetic 503 dependency fault must end as tool_error within bounds, with two attempts. The proof fetches actual Jaeger data after Collector ingestion, checks resources and capture allowlists in Collector JSONL, inspects metric labels and checks synthetic input/baggage/key/document canaries across the specified exported and queried surfaces plus controlled operation logs. It does not establish a universal PII filter, token budget, all fault resilience or production readiness.

Proof-only file exporters are injected into a private copy of the native Collector config under .runtime/local-proof/<run-id>. Their files are bounded by 5 MiB rotation plus one backup. Raw captures, process logs, generated paths and runtime authentication stay outside public source. The command prints the run-folder ID and writes result.json there. Publish a reviewed sanitized summary separately, not the raw directory.

Jaeger uses at most 1000 traces in memory. All data is ephemeral; the runner restarts Jaeger and expects the earlier trace to be absent (404 or an empty result). Collector queues/retries are bounded but not durable. After completion, no owned service remains listening. The small proof does not measure sustained-load retention, performance, outage loss or the P6 coverage target.

The query currently uses Jaeger 2.22's pinned internal HTTP JSON endpoint, suitable for this bounded proof; it is not a stable production monitoring adapter. A future SRE integration must select a supported/versioned read API. Container Compose remains a separate profile; native backend success does not prove Compose or Docker availability.
