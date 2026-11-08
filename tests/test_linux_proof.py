"""Negative acceptance checks for the Docker proof; no Docker or third-party imports."""

import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import prove_linux_backend as proof


def trace(healthy=True):
    names = proof.HEALTHY if healthy else proof.FAULT
    spans = []
    ids = {}
    for index, name in enumerate(names):
        sid = f"{index + 1:016x}"
        parent = ids.get(proof.PARENTS.get(name))
        spans.append(
            {
                "spanID": sid,
                "traceID": "1" * 32,
                "operationName": name,
                "processID": "r" if name in proof.RETRIEVAL else "a",
                "references": []
                if parent is None
                else [{"refType": "CHILD_OF", "traceID": "1" * 32, "spanID": parent}],
                "tags": [],
                "logs": [],
            }
        )
        ids[name] = sid
    processes = {
        pid: {
            "serviceName": service,
            "tags": [{"key": k, "value": v} for k, v in proof.IDENTITY.items()],
        }
        for pid, service in [("a", "policy-agent"), ("r", "policy-retrieval")]
    }
    if healthy:
        for span in spans:
            if span["operationName"] in {
                "POST /v1/ask",
                "tool.retrieve",
                "POST /v1/retrieve",
            }:
                span["tags"].append({"key": "http.status_code", "value": 200})
            if span["operationName"] == "agent.invoke":
                span["tags"] += [
                    {"key": k, "value": v}
                    for k, v in {
                        "lab.outcome": "success",
                        "lab.steps": 3,
                        "lab.tool.calls": 1,
                    }.items()
                ]
    if not healthy:
        for span in spans:
            name = span["operationName"]
            errors = {
                "agent.invoke": "tool_error",
                "tool.retrieve": "tool_unavailable",
                "POST /v1/retrieve": "server_error",
            }
            if name in errors:
                span["tags"].append({"key": "lab.error.type", "value": errors[name]})
            if name in {"tool.retrieve", "POST /v1/retrieve"}:
                span["tags"].append({"key": "http.response.status_code", "value": 503})
    return {"traceID": "1" * 32, "spans": spans, "processes": processes}


class GraphChecks(unittest.TestCase):
    def test_healthy_and_external_parent(self):
        value = trace()
        proof.graph(value, True)
        value["spans"][0]["references"] = [
            {"refType": "CHILD_OF", "traceID": "1" * 32, "spanID": "f" * 16}
        ]
        proof.graph(value, True, "f" * 16)
        with self.assertRaises(ValueError):
            proof.graph(value, True)

    def test_duplicate_id_wrong_parent_service_version_rejected(self):
        for mutate in [
            lambda t: t["spans"][1].update(spanID=t["spans"][0]["spanID"]),
            lambda t: t["spans"][4]["references"][0].update(
                spanID=t["spans"][0]["spanID"]
            ),
            lambda t: t["spans"][4].update(processID="a"),
            lambda t: t["processes"]["a"]["tags"][0].update(value="wrong"),
            lambda t: t["spans"][2].update(
                logs=[{"fields": [{"key": "secret", "value": "x"}]}]
            ),
            lambda t: t["spans"][0].update(traceID="2" * 32),
        ]:
            value = trace()
            mutate(value)
            with self.assertRaises(ValueError):
                proof.graph(value, True)

    def test_fault_requires_errors_and_one_server_per_attempt(self):
        value = trace(False)
        with self.assertRaises(ValueError):
            proof.graph(value, False)
        for span in value["spans"]:
            if span["operationName"] in {
                "agent.invoke",
                "tool.retrieve",
                "POST /v1/retrieve",
            }:
                span["tags"].append({"key": "error", "value": True})
        proof.graph(value, False)
        value["spans"][-1]["references"] = copy.deepcopy(
            value["spans"][-2]["references"]
        )
        with self.assertRaises(ValueError):
            proof.graph(value, False)


class SafetyChecks(unittest.TestCase):
    def test_refuses_exposed_ports_and_unsafe_container_settings(self):
        value = proof.test_service()
        proof.safe_services({"agent": value})
        for field, unsafe in [
            ("ports", [{"host_ip": "0.0.0.0", "published": "18080", "target": 8080}]),
            ("privileged", True),
            ("network_mode", "host"),
            ("read_only", False),
            ("mem_limit", 0),
            ("cpus", 0),
            ("cap_drop", []),
            ("security_opt", []),
        ]:
            altered = copy.deepcopy(value)
            altered[field] = unsafe
            with self.assertRaises(ValueError):
                proof.safe_services({"agent": altered})

    def test_canary_checked_on_every_surface_including_answer(self):
        surfaces = {"trace": "{}", "metric": "{}", "query": "{}", "logs": ""}
        proof.canaries(surfaces, ["submitted question", "generated answer"])
        for name in surfaces:
            with self.assertRaises(ValueError):
                proof.canaries(
                    {**surfaces, name: "generated answer"}, ["generated answer"]
                )

    def test_real_metric_exemplar_shape_without_payload(self):
        exemplar = {
            "timeUnixNano": "1794100466737669629",
            "asDouble": 0.01,
            "traceId": "1" * 32,
            "spanId": "2" * 16,
        }

        def check(value):
            proof.metric_safe({"histogram": {"dataPoints": [{"exemplars": [value]}]}})

        check(exemplar)
        for changed in (
            {"filteredAttributes": [{"key": "question"}]},
            {"unexpected": "payload"},
            {"traceId": "payload"},
            {"asDouble": "payload"},
            {"spanId": "0" * 16},
        ):
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                check({**exemplar, **changed})

    def test_export_rejects_status_text_events_links_and_metric_labels(self):
        span = {"attributes": [], "status": {}}
        proof.span_safe(span)
        for field, value in [
            ("status", {"message": "secret"}),
            ("events", [{}]),
            ("links", [{}]),
            ("attributes", [{"key": "question", "value": {"stringValue": "x"}}]),
        ]:
            with self.assertRaises(ValueError):
                proof.span_safe({**span, field: value})
        with self.assertRaises(ValueError):
            proof.metric_safe(
                {"sum": {"dataPoints": [{"attributes": [{"key": "question"}]}]}}
            )


class IsolationChecks(unittest.TestCase):
    def test_rendered_network_names_cannot_reuse_another_project(self):
        config = {
            "name": "old",
            "networks": {"default": {"name": "old_default"}},
            "services": {"agent": proof.test_service()},
        }
        proof.isolate(config, "ai-proof-example")
        self.assertEqual(
            config["networks"]["default"]["name"], "ai-proof-example_default"
        )
        with self.assertRaises(ValueError):
            proof.isolate(
                {"networks": {"shared": {"external": True}}}, "ai-proof-example"
            )

    def test_validator_failure_also_runs_owned_cleanup(self):
        import tempfile
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary) / "example"
            folder.mkdir()
            services = {
                n: proof.test_service()
                for n in ("agent", "retrieval", "collector", "jaeger")
            }
            for n in ("collector", "jaeger"):
                services[n]["image"] = "example@sha256:" + "1" * 64
            info = {
                "SecurityOptions": ["name=rootless"],
                "OSType": "linux",
                "Architecture": "x86_64",
                "MemoryLimit": True,
                "CpuCfsQuota": True,
                "ServerVersion": "test",
            }
            import json

            with (
                patch.object(proof, "Commands") as cls,
                patch.object(proof, "ports_free", return_value=True),
                patch.object(proof, "private_configs"),
                patch.object(proof, "attributes", return_value=proof.SPAN_ATTRIBUTES),
            ):
                command = cls.return_value
                command.run.side_effect = [
                    json.dumps(info),
                    "test",
                    json.dumps({"services": services}),
                    "",
                    "",
                    "",
                ]

                def compose(*args, **kwargs):
                    if args[0] == "run":
                        raise ValueError("validator failed")
                    return ""

                command.compose.side_effect = compose
                result = proof.execute(folder)
                self.assertEqual(result["status"], "failed")
                self.assertEqual(result.get("failure"), "validator failed")
                self.assertTrue(
                    any(c.args[0] == "down" for c in command.compose.call_args_list)
                )


class FaultStatusChecks(unittest.TestCase):
    def test_jaeger_222_translated_fault_status(self):
        # Sanitized shape of parent-query-capture/fault.json: Jaeger translates
        # the OTel response key to an int64 legacy tag; Collector stays OTel.
        value = trace(False)
        for span in value["spans"]:
            if span["operationName"] in {
                "agent.invoke",
                "tool.retrieve",
                "POST /v1/retrieve",
            }:
                span["tags"].append({"key": "error", "type": "bool", "value": True})
            for tag in span["tags"]:
                if tag["key"] == "http.response.status_code":
                    tag.update(key="http.status_code", type="int64")
        proof.graph(value, False)
        target = value["spans"][-1]
        original = copy.deepcopy(target["tags"])
        for key in ("http.status_code", "http.response.status_code"):
            for bad in (200, 429, 500, "503", True, None):
                target["tags"] = copy.deepcopy(original)
                target["tags"].append({"key": key, "type": "int64", "value": bad})
                with self.subTest(key=key, bad=bad), self.assertRaises(ValueError):
                    proof.graph(value, False)
        target["tags"] = copy.deepcopy(original)
        target["tags"].append(
            {"key": "http.response.status_code", "type": "int64", "value": 503}
        )
        proof.graph(value, False)

    def test_fault_server_must_be_503_and_status_fields_bounded(self):
        value = trace(False)
        for span in value["spans"]:
            name = span["operationName"]
            if name in {"agent.invoke", "tool.retrieve", "POST /v1/retrieve"}:
                span["tags"] = [
                    {"key": "error", "value": True},
                    {
                        "key": "lab.error.type",
                        "value": "tool_error"
                        if name == "agent.invoke"
                        else "tool_unavailable"
                        if name == "tool.retrieve"
                        else "server_error",
                    },
                ]
            if name in {"tool.retrieve", "POST /v1/retrieve"}:
                span["tags"].append({"key": "http.response.status_code", "value": 503})
        proof.graph(value, False)
        value["spans"][-1]["tags"][-1]["value"] = 429
        with self.assertRaises(ValueError):
            proof.graph(value, False)
        with self.assertRaises(ValueError):
            proof.span_safe({"status": {"code": 99}})


class StandaloneChecks(unittest.TestCase):
    def test_span_checks_do_not_require_sibling_checkout_in_lab_ci(self):
        import tempfile
        from unittest.mock import patch

        with (
            tempfile.TemporaryDirectory() as folder,
            patch.object(proof, "BASE", Path(folder)),
        ):
            proof.span_safe({"attributes": []})


if __name__ == "__main__":
    unittest.main()
