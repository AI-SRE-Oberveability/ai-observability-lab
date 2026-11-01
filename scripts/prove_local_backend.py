"""One-shot Windows loopback proof; run with the locked workload Python environment."""

from __future__ import annotations

import hashlib
import json
import logging
import os
import secrets
import socket
import subprocess
import sys
import threading
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import ProxyHandler, build_opener

import uvicorn
import yaml

BASE = Path(__file__).resolve().parents[2]
LAB = BASE / "ai-observability-lab"
CONFIG = BASE / "ai-observability-config/local/native"
PORTS = (14317, 14318, 16685, 16686, 18888, 18889, 18080, 18081)
HTTP = build_opener(ProxyHandler({}))


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def get(url):
    with HTTP.open(url, timeout=2) as response:
        return response.read()


def wait_for(check, description, timeout=30):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            result = check()
            if result:
                return result
        except (OSError, ValueError, URLError):
            pass
        time.sleep(0.1)
    raise RuntimeError("Readiness failed: " + description)


def listeners_closed():
    for port in PORTS:
        with socket.socket() as sock:
            sock.settimeout(0.2)
            if sock.connect_ex(("127.0.0.1", port)) == 0:
                return False
    return True


@contextmanager
def serve(app, port):
    config = uvicorn.Config(
        app, host="127.0.0.1", port=port, access_log=False, log_level="warning"
    )
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    try:
        wait_for(lambda: server.started or not thread.is_alive(), "HTTP service")
        require(thread.is_alive() and server.started, "HTTP service exited")
        yield
    finally:
        server.should_exit = True
        thread.join(timeout=10)
        require(not thread.is_alive(), "Owned HTTP thread did not stop")


def binary(name):
    lock = json.loads(
        (CONFIG.parent / "windows-binaries.lock.json").read_text(encoding="utf-8")
    )
    item = lock[name]
    folder = BASE / ".runtime/backends" / name
    archive = folder / item["url"].rsplit("/", 1)[1]
    exe = folder / ("jaeger.exe" if name == "jaeger" else "otelcol-contrib.exe")
    require(archive.is_file() and exe.is_file(), "Run install_local_backends.py first")
    with archive.open("rb") as stream:
        require(
            hashlib.file_digest(stream, "sha256").hexdigest() == item["sha256"],
            "Archive hash",
        )
    # Compare executable bytes to the verified package, not just a neighbouring archive.
    if name == "jaeger":
        import zipfile

        with zipfile.ZipFile(archive) as package:
            members = [n for n in package.namelist() if n.endswith("/jaeger.exe")]
            require(len(members) == 1, "Jaeger archive layout")
            expected = hashlib.sha256(package.read(members[0])).hexdigest()
    else:
        import tarfile

        with tarfile.open(archive) as package:
            members = [m for m in package if Path(m.name).name == "otelcol-contrib.exe"]
            require(len(members) == 1, "Collector archive layout")
            with package.extractfile(members[0]) as stream:
                expected = hashlib.file_digest(stream, "sha256").hexdigest()
    with exe.open("rb") as stream:
        require(
            hashlib.file_digest(stream, "sha256").hexdigest() == expected,
            "Executable hash",
        )
    return exe, item["version"]


def start(exe, config, run_dir, name, owned):
    log = (run_dir / (name + ".log")).open("wb")
    try:
        process = subprocess.Popen(
            [str(exe), "--config=" + str(config)],
            stdout=log,
            stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
    except BaseException:
        log.close()
        raise
    owned.append((process, log))
    return process


def stop(owned):
    for process, log in reversed(owned):
        if process.poll() is None:
            process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
        log.close()
    owned.clear()


def backend_trace(trace_id, expected_count):
    def fetch():
        payload = json.loads(get("http://127.0.0.1:16686/api/traces/" + trace_id))
        data = payload.get("data") or []
        if data and len(data[0]["spans"]) == expected_count:
            return data[0]
        return None

    return wait_for(fetch, "backend trace " + trace_id, timeout=15)


def graph(trace, healthy):
    spans = trace["spans"]
    expected = (
        [
            "POST /v1/ask",
            "agent.invoke",
            "model.plan",
            "tool.retrieve",
            "POST /v1/retrieve",
            "retrieval.search",
            "model.generate",
        ]
        if healthy
        else [
            "POST /v1/ask",
            "agent.invoke",
            "model.plan",
            "tool.retrieve",
            "tool.retrieve",
            "POST /v1/retrieve",
            "POST /v1/retrieve",
        ]
    )
    require(
        sorted(s["operationName"] for s in spans) == sorted(expected),
        "Exact span names",
    )
    by_id = {s["spanID"]: s for s in spans}
    parents = {
        "agent.invoke": "POST /v1/ask",
        "model.plan": "agent.invoke",
        "tool.retrieve": "agent.invoke",
        "POST /v1/retrieve": "tool.retrieve",
        "retrieval.search": "POST /v1/retrieve",
        "model.generate": "agent.invoke",
    }
    edges = []
    for span in spans:
        name = span["operationName"]
        references = [
            r for r in span.get("references", []) if r["refType"] == "CHILD_OF"
        ]
        if name == "POST /v1/ask":
            require(not references, "Unexpected external trace parent")
        else:
            require(len(references) == 1, "One parent required")
            parent = by_id[references[0]["spanID"]]["operationName"]
            require(parent == parents[name], "Parent edge mismatch")
            edges.append([parent, name])
    services = {p["serviceName"] for p in trace["processes"].values()}
    require(services == {"policy-agent", "policy-retrieval"}, "Two service identities")
    return {
        "trace_id": trace["traceID"],
        "span_count": len(spans),
        "services": sorted(services),
        "names": expected,
        "edges": edges,
    }


def capture_checks(run_dir, traces, forbidden):
    trace_file = run_dir / "traces.jsonl"
    metric_file = run_dir / "metrics.jsonl"
    wait_for(
        lambda: (
            trace_file.exists()
            and metric_file.exists()
            and metric_file.stat().st_size > 0
        ),
        "file exporters",
    )
    prometheus = get("http://127.0.0.1:18889/metrics").decode()
    internal = get("http://127.0.0.1:18888/metrics").decode()
    content = "\n".join(
        [
            trace_file.read_text(encoding="utf-8"),
            metric_file.read_text(encoding="utf-8"),
            (run_dir / "operations.log").read_text(encoding="utf-8"),
            json.dumps(traces),
            prometheus,
            internal,
        ]
    )
    require(
        all(value not in content for value in forbidden), "Prohibited canary exported"
    )
    from ai_lab.telemetry import ATTRIBUTES

    resources = {
        "service.name",
        "service.namespace",
        "service.version",
        "deployment.environment.name",
        "lab.schema.version",
    }
    seen = set()
    for line in trace_file.read_text(encoding="utf-8").splitlines():
        for resource in json.loads(line).get("resourceSpans", []):
            attrs = resource["resource"].get("attributes", [])
            require({a["key"] for a in attrs} <= resources, "Resource allowlist")
            require(
                any(a["key"] == "service.version" for a in attrs), "Version missing"
            )
            for scope in resource.get("scopeSpans", []):
                for span in scope.get("spans", []):
                    require(
                        {a["key"] for a in span.get("attributes", [])} <= ATTRIBUTES,
                        "Span allowlist",
                    )
                    require(
                        not span.get("events") and not span.get("links"),
                        "Event/link capture",
                    )
                    seen.add(span["traceId"].lower())
    for line in metric_file.read_text(encoding="utf-8").splitlines():
        for resource in json.loads(line).get("resourceMetrics", []):
            require(
                {a["key"] for a in resource["resource"].get("attributes", [])}
                <= resources,
                "Metric resource allowlist",
            )
            for scope in resource.get("scopeMetrics", []):
                for metric in scope.get("metrics", []):
                    for kind in ("sum", "histogram", "gauge", "exponentialHistogram"):
                        for point in metric.get(kind, {}).get("dataPoints", []):
                            require(
                                {a["key"] for a in point.get("attributes", [])}
                                <= {"lab.operation", "lab.outcome"},
                                "Metric labels",
                            )
    require("lab_operation" in prometheus, "Application metrics absent")
    require(len(seen) >= 2, "File capture missing trace cohort")
    return {
        "canary_values_found": 0,
        "resource_span_metric_allowlists": "passed",
        "events_and_links": "absent",
        "surfaces": [
            "Collector trace JSONL",
            "Collector metrics JSONL",
            "Jaeger retrieved traces",
            "Prometheus exposition",
            "Collector internal metrics",
            "controlled application operation log",
        ],
        "log_pipeline_exported": False,
    }


def main():
    require(
        os.name == "nt", "This profile requires Windows; use Compose on other hosts"
    )
    require(
        listeners_closed(), "An expected port has a listener; no process was stopped"
    )
    sys.path.insert(0, str(BASE / "ai-agent-workloads/src"))
    import httpx
    from ai_lab.agent import create_app as agent_app
    from ai_lab.retrieval import create_app as retrieval_app
    from ai_lab.settings import Settings

    run_dir = BASE / ".runtime/local-proof" / uuid.uuid4().hex
    run_dir.mkdir(parents=True)
    collector, collector_version = binary("collector")
    jaeger, jaeger_version = binary("jaeger")
    config = yaml.safe_load((CONFIG / "collector.yaml").read_text(encoding="utf-8"))
    for signal in ("traces", "metrics"):
        name = "file/" + signal
        config["exporters"][name] = {
            "path": str(run_dir / (signal + ".jsonl")),
            "format": "json",
            "flush_interval": "200ms",
            "rotation": {"max_megabytes": 5, "max_backups": 1},
        }
        config["service"]["pipelines"][signal]["exporters"].append(name)
    capture_config = run_dir / "collector.yaml"
    capture_config.write_text(
        yaml.safe_dump(config, sort_keys=False), encoding="utf-8", newline="\n"
    )
    subprocess.run(
        [str(collector), "validate", "--config=" + str(capture_config)],
        check=True,
        timeout=45,
        capture_output=True,
    )
    key = secrets.token_urlsafe(32)
    question_canary = "SYNTHETIC_INPUT_CANARY_" + uuid.uuid4().hex
    baggage_canary = "SYNTHETIC_BAGGAGE_CANARY_" + uuid.uuid4().hex
    handler = logging.FileHandler(run_dir / "operations.log", encoding="utf-8")
    logger = logging.getLogger("ai_lab.operational")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    owned = []
    report = {
        "date": datetime.now(timezone(timedelta(hours=4))).isoformat(),
        "profile": "Windows loopback, deterministic mock, ephemeral memory",
        "versions": {"collector": collector_version, "jaeger": jaeger_version},
        "query_api": "Jaeger 2.22 pinned internal HTTP API; not a production adapter",
        "azure_operations": False,
        "gitlab_changes": False,
    }
    try:
        start(jaeger, CONFIG / "jaeger.yaml", run_dir, "jaeger", owned)
        wait_for(lambda: get("http://127.0.0.1:16686/"), "Jaeger HTTP")
        start(collector, capture_config, run_dir, "collector", owned)
        wait_for(lambda: get("http://127.0.0.1:18888/metrics"), "Collector metrics")
        common = {
            "allow_faults": True,
            "otlp_endpoint": "http://127.0.0.1:14318",
            "version": "0.1.0-local-proof",
        }
        tool = retrieval_app(Settings(key, **common))
        agent = agent_app(
            Settings(key, retrieval_url="http://127.0.0.1:18081", **common)
        )
        with (
            serve(tool, 18081),
            serve(agent, 18080),
            httpx.Client(trust_env=False) as client,
        ):
            headers = {"X-Lab-Key": key, "baggage": "private=" + baggage_canary}
            healthy = client.post(
                "http://127.0.0.1:18080/v1/ask",
                headers=headers,
                json={"question": "How to apply for repair " + question_canary},
                timeout=6,
            )
            require(healthy.status_code == 200, "Healthy HTTP response")
            healthy = healthy.json()
            require(
                healthy["outcome"] == "success" and healthy["citations"], "Cited answer"
            )
            require(
                healthy["usage"] == {"input_tokens": None, "output_tokens": None},
                "Mock usage",
            )
            started = time.monotonic()
            fault = client.post(
                "http://127.0.0.1:18080/v1/ask",
                headers=headers,
                json={"question": "repair", "scenario": "server_error"},
                timeout=6,
            )
            elapsed = time.monotonic() - started
            require(fault.status_code == 200, "Fault HTTP response")
            fault = fault.json()
            require(
                fault["outcome"] == "tool_error"
                and fault["tool_calls"] == 2
                and elapsed < 2.5,
                "Bounded fault outcome",
            )
            tool.state.telemetry.flush()
            agent.state.telemetry.flush()
        healthy_trace = backend_trace(healthy["trace_id"], 7)
        fault_trace = backend_trace(fault["trace_id"], 7)
        report["healthy"] = graph(healthy_trace, True)
        report["fault"] = {
            **graph(fault_trace, False),
            "outcome": fault["outcome"],
            "tool_calls": fault["tool_calls"],
            "elapsed_seconds": round(elapsed, 4),
        }
        policies = json.loads(
            (BASE / "ai-agent-workloads/src/ai_lab/policies.json").read_text()
        )
        report["privacy"] = capture_checks(
            run_dir,
            [healthy_trace, fault_trace],
            [key, question_canary, baggage_canary]
            + [p["text"] for p in policies.values()],
        )
        stop(owned)
        require(
            wait_for(listeners_closed, "owned listeners stopped", timeout=10), "Cleanup"
        )
        start(jaeger, CONFIG / "jaeger.yaml", run_dir, "jaeger-restart", owned)
        wait_for(lambda: get("http://127.0.0.1:16686/"), "Jaeger restart")
        try:
            old = json.loads(
                get("http://127.0.0.1:16686/api/traces/" + healthy["trace_id"])
            )
            report["restart_trace_http_status"] = 200
        except HTTPError as error:
            if error.code != 404:
                raise
            old = {"data": []}
            report["restart_trace_http_status"] = 404
        require(not old.get("data"), "Old trace unexpectedly retained")
        report["ephemeral_retention_after_restart"] = "old trace absent"
    finally:
        stop(owned)
        logger.removeHandler(handler)
        handler.close()
        report["owned_ports_released"] = wait_for(
            listeners_closed, "final cleanup", timeout=10
        )
        (run_dir / "result.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
    require(
        report.get("ephemeral_retention_after_restart") == "old trace absent",
        "Incomplete proof",
    )
    report["status"] = "passed"
    (run_dir / "result.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(
        json.dumps(
            {
                "status": "passed",
                "runtime_folder": run_dir.name,
                "healthy_spans": 7,
                "fault_spans": 7,
                "ports_released": True,
            }
        )
    )


if __name__ == "__main__":
    main()
