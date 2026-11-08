"""Bounded rootless Linux Compose proof. Standard library only; raw output stays private."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import os
import platform
import re
import secrets
import signal as process_signal
import socket
import subprocess
import time
import uuid
from collections import Counter
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import ProxyHandler, Request, build_opener

LAB = Path(__file__).resolve().parents[1]
BASE = LAB.parent
IDENTITY = {
    "service.namespace": "personal-ai-lab",
    "service.version": "0.1.0-linux-proof",
    "deployment.environment.name": "local",
    "lab.schema.version": "1.0.0",
}
RESOURCES = {"service.name", *IDENTITY}
# Proof assertion schema mirrors contract 1.0.0; runtime checks it against the actual
# workload source before starting containers. Unit checks need no sibling checkout.
SPAN_ATTRIBUTES = {
    "http.request.method",
    "http.route",
    "http.response.status_code",
    "lab.operation",
    "lab.outcome",
    "lab.model.mode",
    "lab.model.name",
    "lab.steps",
    "lab.tool.calls",
    "lab.retry",
    "lab.retrieval.count",
    "lab.error.type",
    "lab.schema.version",
}
RETRIEVAL = {"POST /v1/retrieve", "retrieval.search"}
HEALTHY = [
    "POST /v1/ask",
    "agent.invoke",
    "model.plan",
    "tool.retrieve",
    "POST /v1/retrieve",
    "retrieval.search",
    "model.generate",
]
FAULT = [
    "POST /v1/ask",
    "agent.invoke",
    "model.plan",
    "tool.retrieve",
    "POST /v1/retrieve",
    "tool.retrieve",
    "POST /v1/retrieve",
]
PARENTS = {
    "agent.invoke": "POST /v1/ask",
    "model.plan": "agent.invoke",
    "tool.retrieve": "agent.invoke",
    "POST /v1/retrieve": "tool.retrieve",
    "retrieval.search": "POST /v1/retrieve",
    "model.generate": "agent.invoke",
}
PORTS = (18080, 16686, 18888, 18889)
HTTP = build_opener(ProxyHandler({}))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def attributes():
    # Read the reviewed contract without importing application dependencies.
    tree = ast.parse((BASE / "ai-agent-workloads/src/ai_lab/telemetry.py").read_text())
    node = next(
        n
        for n in tree.body
        if isinstance(n, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "ATTRIBUTES" for t in n.targets)
    )
    return set(ast.literal_eval(node.value.args[0]))


def span_safe(span):
    require(
        {a["key"] for a in span.get("attributes", [])} <= SPAN_ATTRIBUTES,
        "Span allowlist",
    )
    require(not span.get("events") and not span.get("links"), "Event/link capture")
    require(not span.get("status", {}).get("message"), "Status description capture")
    require(span.get("status", {}).get("code", 0) in (0, 1, 2), "Unknown span status")


def metric_safe(metric):
    for kind in ("sum", "histogram", "gauge", "exponentialHistogram", "summary"):
        for point in metric.get(kind, {}).get("dataPoints", []):
            require(
                {a["key"] for a in point.get("attributes", [])}
                <= {"lab.operation", "lab.outcome"},
                "Metric labels",
            )
            for exemplar in point.get("exemplars", []):
                require(
                    set(exemplar)
                    <= {
                        "timeUnixNano",
                        "asDouble",
                        "asInt",
                        "traceId",
                        "spanId",
                        "filteredAttributes",
                    }
                    and not exemplar.get("filteredAttributes"),
                    "Metric exemplar allowlist",
                )
                require(
                    all(
                        isinstance(exemplar.get(key), str)
                        and re.fullmatch("[0-9a-f]{" + str(length) + "}", exemplar[key])
                        and int(exemplar[key], 16) != 0
                        for key, length in (("traceId", 32), ("spanId", 16))
                    )
                    and isinstance(exemplar.get("timeUnixNano"), str)
                    and re.fullmatch(r"[0-9]{1,20}", exemplar["timeUnixNano"]),
                    "Metric exemplar identity/time",
                )
                values = [key for key in ("asDouble", "asInt") if key in exemplar]
                require(len(values) == 1, "Metric exemplar numeric sample")
                value = exemplar[values[0]]
                require(
                    (
                        values[0] == "asDouble"
                        and type(value) in (int, float)
                        and math.isfinite(value)
                    )
                    or (
                        values[0] == "asInt"
                        and isinstance(value, str)
                        and re.fullmatch(r"-?[0-9]{1,20}", value)
                    ),
                    "Metric exemplar numeric sample",
                )


def canaries(surfaces, forbidden):
    require(all(forbidden), "Empty privacy canary")
    for name, content in surfaces.items():
        require(
            all(value not in content for value in forbidden),
            "Canary on surface: " + name,
        )


def privacy_values(key, question, marker, baggage, answers, documents):
    return [key, question, marker, baggage, *answers, *documents]


def queried_trace(payload, requested):
    data = payload.get("data") or []
    if not data:
        return None
    require(
        len(data) == 1 and data[0]["traceID"] == requested, "Queried cohort identity"
    )
    return data[0] if len(data[0]["spans"]) == 7 else None


def retrieval_ready(commands):
    def probe():
        try:
            return (
                commands.compose(
                    "exec",
                    "-T",
                    "retrieval",
                    "python",
                    "-c",
                    "from urllib.request import urlopen; urlopen('http://127.0.0.1:8080/healthz', timeout=2).read()",
                    timeout=5,
                )
                or True
            )
        except ValueError:
            return False

    wait(probe, "private retrieval healthz", 30)


def cleanup(commands):
    errors = []
    for attempt in range(3):
        try:
            commands.compose(
                "down", "--volumes", "--remove-orphans", "--timeout", "10", timeout=45
            )
        except ValueError as error:
            errors.append(str(error))
        remaining = []
        for prefix in (["ps", "-aq"], ["network", "ls", "-q"], ["volume", "ls", "-q"]):
            try:
                remaining.append(
                    commands.run(
                        [
                            "docker",
                            "--context",
                            "rootless",
                            *prefix,
                            "--filter",
                            "label=com.docker.compose.project=" + commands.project,
                        ],
                        timeout=15,
                    ).strip()
                )
            except ValueError as error:
                remaining.append("inspection failed")
                errors.append(str(error))
        released = ports_free()
        if not any(remaining) and released:
            return (
                "owned containers/networks/volumes absent; ports released; down errors="
                + str(len(errors))
            )
    raise ValueError(
        "Cleanup verification failed after bounded retries; owned resources present="
        + str(any(remaining))
        + "; ports released="
        + str(released)
        + "; "
        + "; ".join(errors)
    )


def graph(trace, healthy, external_parent=None):
    spans = trace["spans"]
    require(
        sorted(s["operationName"] for s in spans)
        == sorted(HEALTHY if healthy else FAULT),
        "Exact seven-span graph",
    )
    by_id = {s["spanID"]: s for s in spans}
    require(len(by_id) == 7, "Duplicate span ID")
    clients = set()
    servers = set()
    for span in spans:
        name = span["operationName"]
        require(span["traceID"] == trace["traceID"], "Trace continuity")
        process = trace["processes"][span["processID"]]
        require(
            process["serviceName"]
            == ("policy-retrieval" if name in RETRIEVAL else "policy-agent"),
            "Span service ownership",
        )
        tags = {t["key"]: t["value"] for t in process.get("tags", [])}
        require(all(tags.get(k) == v for k, v in IDENTITY.items()), "Resource identity")
        require(not span.get("logs"), "Jaeger span event capture")
        tags = {t["key"]: t["value"] for t in span.get("tags", [])}
        require(not tags.get("otel.status_description"), "Jaeger status text")
        if healthy:
            require(
                all(
                    type(t["value"]) is int and t["value"] == 200
                    for t in span.get("tags", [])
                    if t["key"] in {"http.status_code", "http.response.status_code"}
                ),
                "Unexpected healthy HTTP status",
            )
            require(
                all(
                    t["value"] is False
                    for t in span.get("tags", [])
                    if t["key"] == "error"
                ),
                "Healthy error marker",
            )
            require(
                all(
                    t["value"] in ("OK", "UNSET", 0, 1)
                    for t in span.get("tags", [])
                    if t["key"] == "otel.status_code"
                ),
                "Healthy error status",
            )
            require(not tags.get("lab.error.type"), "Healthy typed error")
            if name in {"POST /v1/ask", "tool.retrieve", "POST /v1/retrieve"}:
                statuses = [
                    t["value"]
                    for t in span.get("tags", [])
                    if t["key"] in {"http.status_code", "http.response.status_code"}
                ]
                require(
                    bool(statuses)
                    and all(type(v) is int and v == 200 for v in statuses),
                    "Healthy HTTP status",
                )
            if name == "agent.invoke":
                for key, expected in {
                    "lab.outcome": "success",
                    "lab.steps": 3,
                    "lab.tool.calls": 1,
                }.items():
                    values = [
                        t["value"] for t in span.get("tags", []) if t["key"] == key
                    ]
                    require(
                        bool(values)
                        and all(
                            type(v) is type(expected) and v == expected for v in values
                        ),
                        "Healthy agent bounds/outcome",
                    )
        if not healthy and name in {
            "agent.invoke",
            "tool.retrieve",
            "POST /v1/retrieve",
        }:
            require(tags.get("error") is True, "Fault span status")
            expected_error = {
                "agent.invoke": "tool_error",
                "tool.retrieve": "tool_unavailable",
                "POST /v1/retrieve": "server_error",
            }[name]
            require(tags.get("lab.error.type") == expected_error, "Typed fault status")
            if name != "agent.invoke":
                require(
                    bool(
                        statuses := [
                            tag["value"]
                            for tag in span.get("tags", [])
                            if tag["key"]
                            in {"http.response.status_code", "http.status_code"}
                        ]
                    )
                    and all(type(value) is int and value == 503 for value in statuses),
                    "Controlled retrieval 503",
                )
        refs = span.get("references", [])
        if name == "POST /v1/ask" and external_parent is None:
            require(not refs, "Unexpected external parent")
            continue
        require(
            len(refs) == 1
            and refs[0]["refType"] == "CHILD_OF"
            and refs[0]["traceID"] == trace["traceID"],
            "One same-trace parent",
        )
        parent = refs[0]["spanID"]
        if name == "POST /v1/ask":
            require(parent == external_parent, "External W3C parent")
        else:
            require(
                parent in by_id and by_id[parent]["operationName"] == PARENTS[name],
                "Parent edge",
            )
        if name == "tool.retrieve":
            clients.add(span["spanID"])
        if name == "POST /v1/retrieve":
            require(parent not in servers, "Duplicate server for client attempt")
            servers.add(parent)
    require(clients == servers, "Inter-service W3C edges")
    return {
        "span_count": 7,
        "names": [s["operationName"] for s in spans],
        "exact_parents_services_identity_status": "passed",
        "external_w3c": bool(external_parent),
    }


def test_service():
    """Small valid safety fixture, also documents runner-required controls."""
    return {
        "ports": [],
        "read_only": True,
        "mem_limit": "256m",
        "cpus": 1,
        "cap_drop": ["ALL"],
        "security_opt": ["no-new-privileges:true"],
        "logging": {
            "driver": "json-file",
            "options": {"max-size": "5m", "max-file": "2"},
        },
    }


def safe_services(services):
    for name, service in services.items():
        require(
            not service.get("privileged") and not service.get("network_mode"),
            "Unsafe network/privilege",
        )
        require(service.get("read_only") is True, "Read-only rootfs: " + name)
        require(
            service.get("mem_limit") and float(service.get("cpus", 0)) > 0,
            "Resource bounds",
        )
        require(
            "ALL" in service.get("cap_drop", [])
            and "no-new-privileges:true" in service.get("security_opt", []),
            "Privilege bounds",
        )
        require(service.get("logging") == test_service()["logging"], "Log bounds")
        for port in service.get("ports", []):
            require(
                isinstance(port, dict) and port.get("host_ip") == "127.0.0.1",
                "Host port must be loopback",
            )


def isolate(config, project):
    require(
        project.startswith("ai-proof-") and project.replace("-", "").isalnum(),
        "Owned project name",
    )
    config["name"] = project
    for kind in ("networks", "volumes"):
        for name, resource in config.get(kind, {}).items():
            require(
                not resource.get("external"),
                "External resource outside proof ownership",
            )
            resource["name"] = project + "_" + name
    for service in config.get("services", {}).values():
        require(
            not service.get("container_name"),
            "Fixed container name outside proof ownership",
        )


def wait(check, description, timeout=30):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            result = check()
            if result:
                return result
        except (OSError, ValueError, URLError):
            pass
        time.sleep(0.2)
    raise ValueError("Readiness timeout: " + description)


def http(path, data=None, headers=None):
    request = Request(
        path,
        data=None if data is None else json.dumps(data).encode(),
        headers={
            **({"Content-Type": "application/json"} if data is not None else {}),
            **(headers or {}),
        },
    )
    with HTTP.open(request, timeout=6) as response:
        return response.read().decode()


def ports_free():
    for port in PORTS:
        with socket.socket() as sock:
            sock.settimeout(0.2)
            if sock.connect_ex(("127.0.0.1", port)) == 0:
                return False
    return True


class Commands:
    def __init__(self, folder, env, project):
        self.folder, self.env, self.project = folder, env, project
        self.count = 0

    def run(self, args, timeout=60):
        self.count += 1
        stem = self.folder / f"command-{self.count:03}"
        started = time.monotonic()
        process = subprocess.Popen(
            args,
            env=self.env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )
        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except BaseException as error:
            # This PGID belongs exclusively to this child session; never target others.
            try:
                os.killpg(process.pid, process_signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                stdout, stderr = process.communicate(timeout=2)
            except subprocess.TimeoutExpired:
                stdout, stderr = b"", b""
            finally:
                try:
                    os.killpg(process.pid, process_signal.SIGKILL)
                except ProcessLookupError:
                    pass
                stdout, stderr = process.communicate(timeout=2)
                stem.with_suffix(".stdout").write_bytes(stdout)
                stem.with_suffix(".stderr").write_bytes(stderr)
                stem.with_suffix(".json").write_text(
                    json.dumps(
                        {
                            "command": args[:3],
                            "timeout": timeout,
                            "owned_group_terminated": True,
                        }
                    )
                )
            if isinstance(error, subprocess.TimeoutExpired):
                raise ValueError(
                    "Command timed out; private receipt " + stem.name
                ) from None
            raise
        result = subprocess.CompletedProcess(args, process.returncode, stdout, stderr)
        stem.with_suffix(".stdout").write_bytes(result.stdout)
        stem.with_suffix(".stderr").write_bytes(result.stderr)
        stem.with_suffix(".json").write_text(
            json.dumps(
                {
                    "command": args[:3],
                    "exit": result.returncode,
                    "seconds": round(time.monotonic() - started, 3),
                }
            )
        )
        require(result.returncode == 0, "Command failed; private receipt " + stem.name)
        return result.stdout.decode()

    def compose(self, *args, timeout=60):
        return self.run(
            [
                "docker",
                "--context",
                "rootless",
                "compose",
                "-p",
                self.project,
                "-f",
                str(self.folder / "compose.json"),
                *args,
            ],
            timeout,
        )


def private_configs(folder):
    source = (BASE / "ai-observability-config/local/collector.yaml").read_text()
    require(source.count("exporters:\n") == 1, "Collector exporter injection boundary")
    exporters = "".join(
        f"  file/{signal}:\n    path: /capture/{signal}.jsonl\n    format: json\n"
        "    flush_interval: 200ms\n    rotation: {max_megabytes: 5, max_backups: 1}\n"
        for signal in ("traces", "metrics")
    )
    source = source.replace("exporters:\n", "exporters:\n" + exporters)
    for signal, old in [("traces", "otlp_grpc/jaeger"), ("metrics", "prometheus")]:
        require(
            source.count(f"exporters: [{old}]") == 1,
            "Collector pipeline injection boundary",
        )
        source = source.replace(
            f"exporters: [{old}]", f"exporters: [{old}, file/{signal}]"
        )
    (folder / "collector.yaml").write_text(source)
    source = (BASE / "ai-observability-config/local/native/jaeger.yaml").read_text()
    source = source.replace("127.0.0.1:", "0.0.0.0:").replace(":14317", ":4317")
    (folder / "jaeger.yaml").write_text(source)
    (folder / "capture").mkdir(mode=0o700)


def capture(folder, traces, forbidden):
    surfaces = {"Jaeger queries": json.dumps(traces)}
    exported = Counter()
    metrics_seen = set()
    for signal in ("traces", "metrics"):
        paths = sorted((folder / "capture").glob(signal + "*.json*"))
        require(bool(paths), "Missing Collector " + signal + " export")
        surfaces[signal] = "\n".join(p.read_text() for p in paths)
        for line in surfaces[signal].splitlines():
            key, scope_key, item_key = (
                ("resourceSpans", "scopeSpans", "spans")
                if signal == "traces"
                else ("resourceMetrics", "scopeMetrics", "metrics")
            )
            resources = json.loads(line).get(key, [])
            require(bool(resources), "Empty Collector export envelope")
            for resource in resources:
                attrs = {
                    a["key"]: a["value"].get("stringValue")
                    for a in resource["resource"].get("attributes", [])
                }
                require(
                    set(attrs) <= RESOURCES
                    and all(attrs.get(k) == v for k, v in IDENTITY.items())
                    and attrs.get("service.name")
                    in {"policy-agent", "policy-retrieval"},
                    "Export resource identity",
                )
                for scope in resource.get(scope_key, []):
                    require(
                        not scope.get("scope", {}).get("attributes"), "Scope attributes"
                    )
                    for item in scope.get(item_key, []):
                        (span_safe if signal == "traces" else metric_safe)(item)
                        if signal == "traces":
                            exported[
                                (
                                    item["traceId"].lower(),
                                    item["spanId"].lower(),
                                    item["name"],
                                    attrs["service.name"],
                                )
                            ] += 1
                        elif item.get("name") in {
                            "lab.operation.calls",
                            "lab.operation.duration",
                        }:
                            points = [
                                point
                                for kind in ("sum", "histogram")
                                for point in item.get(kind, {}).get("dataPoints", [])
                            ]
                            require(
                                bool(points)
                                and all(
                                    any(
                                        a["key"] == "lab.operation"
                                        and a["value"].get("stringValue")
                                        for a in point.get("attributes", [])
                                    )
                                    for point in points
                                ),
                                "Operation metric data points",
                            )
                            metrics_seen.add((attrs["service.name"], item["name"]))
    expected = Counter(
        (
            t["traceID"],
            span["spanID"],
            span["operationName"],
            t["processes"][span["processID"]]["serviceName"],
        )
        for t in traces
        for span in t["spans"]
    )
    cohort_ids = {t["traceID"] for t in traces}
    require(
        Counter({k: v for k, v in exported.items() if k[0] in cohort_ids}) == expected,
        "Exact exported cohort spans",
    )
    require(
        metrics_seen
        == {
            (service, metric)
            for service in ("policy-agent", "policy-retrieval")
            for metric in ("lab.operation.calls", "lab.operation.duration")
        },
        "Both-service operation metrics missing",
    )
    for name in ("Prometheus", "Collector internal"):
        surfaces[name] = (folder / (name.replace(" ", "-") + ".txt")).read_text()
    require("lab_operation" in surfaces["Prometheus"], "Application metrics absent")
    surfaces["container logs"] = (folder / "containers.log").read_text()
    canaries(surfaces, forbidden)
    return {
        "surfaces": sorted(surfaces),
        "canary_values_found": 0,
        "exact_cohort_export_spans": sum(expected.values()),
        "both_service_operation_metrics": sorted(metrics_seen),
        "allowlists": "passed",
        "log_pipeline_exported": False,
        "controlled_operation_log": "not configured; container stdout/stderr inspected",
    }


def freeze_exports(commands, folder, traces, key):
    commands.compose("stop", "-t", "10", "agent", "retrieval")
    for name, port in [("Prometheus", 18889), ("Collector internal", 18888)]:
        (folder / (name.replace(" ", "-") + ".txt")).write_text(
            http(f"http://127.0.0.1:{port}/metrics")
        )

    def complete():
        try:
            (folder / "containers.log").write_text("")
            capture(folder, traces, [key])
            return True
        except (OSError, ValueError, KeyError):
            return False

    wait(complete, "complete Collector cohorts and both-service metrics", 30)
    commands.compose("stop", "-t", "10", "collector")
    (folder / "containers.log").write_text(commands.compose("logs", "--no-color"))


def finish_cleanup(commands, report):
    try:
        report["cleanup"] = cleanup(commands)
    except Exception as error:
        report["cleanup"] = str(error)
        report["status"] = "failed"


def prepare(config, folder, project):
    require(
        set(config["services"]) == {"agent", "retrieval", "collector", "jaeger"},
        "Expected services only",
    )
    require(attributes() == SPAN_ATTRIBUTES, "Workload capture contract changed")
    private_configs(folder)
    services = config["services"]
    for name in ("agent", "retrieval"):
        services[name]["image"] = project + "-workloads:local"
    for name in ("collector", "jaeger"):
        service = services[name]
        require("@sha256:" in service["image"], "Backend immutable pin")
        service.update(
            read_only=True,
            user="0:0",
            tmpfs=["/tmp"],
            command=["--config=/proof/" + name + ".yaml"],
            volumes=[
                {
                    "type": "bind",
                    "source": str(folder / (name + ".yaml")),
                    "target": "/proof/" + name + ".yaml",
                    "read_only": True,
                }
            ],
        )
    services["collector"]["volumes"].append(
        {"type": "bind", "source": str(folder / "capture"), "target": "/capture"}
    )
    safe_services(services)
    # Private rendered file includes transient auth; never print or publish it.
    isolate(config, project)
    (folder / "compose.json").write_text(json.dumps(config))


def execute(folder):
    project = "ai-proof-" + folder.name
    key = secrets.token_urlsafe(32)
    env = {**os.environ, "LAB_API_KEY": key, "LAB_VERSION": IDENTITY["service.version"]}
    commands = Commands(folder, env, project)
    report = {
        "status": "failed",
        "project": project,
        "profile": "Linux x86-64 rootless Compose",
        "model_mode": "deterministic-mock",
        "azure_operations": False,
        "registry_publication": False,
        "cleanup": "no resources created",
    }
    owned = False
    try:
        report["host"] = {
            "system": platform.system(),
            "architecture": platform.machine(),
            "python": platform.python_version(),
        }
        report["sources"] = {}
        for name, paths in {
            "ai-observability-lab": ["compose.yaml", "scripts/prove_linux_backend.py"],
            "ai-agent-workloads": [
                "Dockerfile",
                "compose.yaml",
                "requirements.lock.txt",
                "src/ai_lab/agent.py",
                "src/ai_lab/retrieval.py",
                "src/ai_lab/telemetry.py",
            ],
            "ai-observability-config": [
                "local/compose.yaml",
                "local/collector.yaml",
                "local/native/jaeger.yaml",
            ],
        }.items():
            repo = BASE / name
            head = subprocess.run(
                ["git", "-C", str(repo), "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            report["sources"][name] = {
                "head": head.stdout.strip() if head.returncode == 0 else "unavailable",
                "files": {
                    p: hashlib.sha256((repo / p).read_bytes()).hexdigest()
                    for p in paths
                    if (repo / p).is_file()
                },
                "acceptance": "working tree bytes; no new CI or publication implied",
            }
        require(
            platform.system() == "Linux" and platform.machine() == "x86_64",
            "Linux x86-64 required",
        )
        info = json.loads(
            commands.run(
                ["docker", "--context", "rootless", "info", "--format", "{{json .}}"]
            )
        )
        require(
            any("rootless" in s for s in info["SecurityOptions"]),
            "Rootless daemon required",
        )
        require(
            info["OSType"] == "linux" and info["Architecture"] == "x86_64",
            "Daemon platform",
        )
        require(
            info.get("MemoryLimit") and info.get("CpuCfsQuota"),
            "Daemon resource limits unsupported",
        )
        require(ports_free(), "Expected port already occupied; nothing stopped")
        report["docker"] = {
            "server": info["ServerVersion"],
            "platform": info["Architecture"],
            "compose": commands.run(
                ["docker", "compose", "version", "--short"]
            ).strip(),
        }
        config = json.loads(
            commands.run(
                [
                    "docker",
                    "--context",
                    "rootless",
                    "compose",
                    "-f",
                    str(LAB / "compose.yaml"),
                    "config",
                    "--format",
                    "json",
                ]
            )
        )
        prepare(config, folder, project)
        commands.compose("config", "--quiet")
        commands.compose("pull", "collector", "jaeger", timeout=180)
        commands.compose("build", "agent", "retrieval", timeout=300)
        owned = True
        commands.compose(
            "run",
            "--rm",
            "--no-deps",
            "collector",
            "validate",
            "--config=/proof/collector.yaml",
        )
        owned = True
        commands.compose("up", "-d", "--no-build", timeout=90)
        wait(lambda: http("http://127.0.0.1:18080/healthz"), "agent")
        wait(lambda: http("http://127.0.0.1:16686/"), "Jaeger")
        wait(lambda: http("http://127.0.0.1:18888/metrics"), "Collector")
        retrieval_ready(commands)
        ids = commands.compose("ps", "-q").split()
        inspection = json.loads(
            commands.run(["docker", "--context", "rootless", "inspect", *ids])
        )
        report["containers"] = []
        for container in inspection:
            host = container["HostConfig"]
            require(
                host["Memory"] > 0 and host["NanoCpus"] > 0, "Actual resource limits"
            )
            require(
                host["ReadonlyRootfs"] and "ALL" in host["CapDrop"], "Actual hardening"
            )
            for mappings in (container["NetworkSettings"].get("Ports") or {}).values():
                require(
                    all(m["HostIp"] == "127.0.0.1" for m in mappings or []),
                    "Actual loopback binding",
                )
            name = container["Config"]["Labels"]["com.docker.compose.service"]
            if name in {"agent", "retrieval"}:
                require(
                    container["Config"]["User"] == "10001:10001",
                    "Nonroot workload user",
                )
            image = json.loads(
                commands.run(
                    [
                        "docker",
                        "--context",
                        "rootless",
                        "image",
                        "inspect",
                        container["Image"],
                    ]
                )
            )[0]
            report["containers"].append(
                {
                    "service": name,
                    "image_id": container["Image"],
                    "platform": image["Os"] + "/" + image["Architecture"],
                    "memory_bytes": host["Memory"],
                    "nano_cpus": host["NanoCpus"],
                    "user": container["Config"]["User"],
                }
            )
        marker = "SYNTHETIC_QUESTION_" + uuid.uuid4().hex
        question = "How to apply for repair " + marker
        baggage = "SYNTHETIC_BAGGAGE_" + uuid.uuid4().hex
        headers = {"X-Lab-Key": key, "baggage": "private=" + baggage}
        traces = []
        answers = []
        for cohort in ("healthy", "fault", "w3c"):
            external_trace, parent = uuid.uuid4().hex, secrets.token_hex(8)
            sent = dict(headers)
            if cohort == "w3c":
                sent["traceparent"] = f"00-{external_trace}-{parent}-01"
            started = time.monotonic()
            response = json.loads(
                http(
                    "http://127.0.0.1:18080/v1/ask",
                    {
                        "question": question,
                        "scenario": "server_error" if cohort == "fault" else "healthy",
                    },
                    sent,
                )
            )
            elapsed = time.monotonic() - started
            require(
                response["model_mode"] == "deterministic-mock"
                and response["usage"] == {"input_tokens": None, "output_tokens": None},
                "Mock usage",
            )
            if cohort == "fault":
                require(
                    response["outcome"] == "tool_error"
                    and response["tool_calls"] == 2
                    and elapsed < 2.5,
                    "Bounded fault",
                )
            else:
                require(
                    response["outcome"] == "success"
                    and response["citations"][0]["document_id"] == "SYN-REPAIR-001",
                    "Cited healthy answer",
                )
            if cohort == "w3c":
                require(response["trace_id"] == external_trace, "W3C trace continuity")
            answers.append(response["answer"])

            def fetch():
                raw = http("http://127.0.0.1:16686/api/traces/" + response["trace_id"])
                (folder / ("query-" + cohort + ".json")).write_text(raw)
                payload = json.loads(raw)
                return queried_trace(payload, response["trace_id"])

            trace = wait(fetch, "Jaeger " + cohort, 20)
            traces.append(trace)
            # Persist private query data before graph assertions can fail.
            (folder / "queries.json").write_text(json.dumps(traces))
            report[cohort] = {
                **graph(trace, cohort != "fault", parent if cohort == "w3c" else None),
                "outcome": response["outcome"],
                "tool_calls": response["tool_calls"],
                "seconds": round(elapsed, 4),
            }
        (folder / "queries.json").write_text(json.dumps(traces))
        freeze_exports(commands, folder, traces, key)
        policies = json.loads(
            (BASE / "ai-agent-workloads/src/ai_lab/policies.json").read_text()
        )
        report["privacy"] = capture(
            folder,
            traces,
            privacy_values(
                key,
                question,
                marker,
                baggage,
                answers,
                [p["text"] for p in policies.values()],
            ),
        )
        commands.compose("restart", "-t", "10", "jaeger")
        wait(lambda: http("http://127.0.0.1:16686/"), "Jaeger restart")
        try:
            old = json.loads(
                http("http://127.0.0.1:16686/api/traces/" + traces[0]["traceID"])
            )
        except HTTPError as error:
            require(error.code == 404, "Unexpected query HTTP error")
            old = {"data": []}
        require(not old.get("data"), "Ephemeral memory retention")
        report["ephemeral_restart"] = "old trace absent"
        report["status"] = "passed"
    except (Exception, KeyboardInterrupt) as error:
        report["failure"] = str(error)
    finally:
        if owned:
            finish_cleanup(commands, report)
        (folder / "result.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--runtime-root", type=Path, default=BASE / ".runtime/linux-proof"
    )
    args = parser.parse_args()
    os.umask(0o077)
    root = args.runtime_root.resolve()
    require(
        ".runtime" in root.parts
        and not any(
            root.is_relative_to(BASE / name)
            for name in (
                "ai-observability-lab",
                "ai-agent-workloads",
                "ai-observability-config",
                "AI-Observability-Infra",
            )
        ),
        "Runtime must be outside public repositories under .runtime",
    )
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    require(root.stat().st_mode & 0o077 == 0, "Runtime root must be private (0700)")
    folder = root / uuid.uuid4().hex
    folder.mkdir(mode=0o700)

    def cancelled(signum, frame):
        raise KeyboardInterrupt("SIGTERM cancellation")

    process_signal.signal(process_signal.SIGTERM, cancelled)
    report = execute(folder)
    print(
        json.dumps(
            {
                "status": report["status"],
                "runtime_folder": folder.name,
                "cleanup": report["cleanup"],
            }
        )
    )
    raise SystemExit(0 if report["status"] == "passed" else 1)


if __name__ == "__main__":
    main()
