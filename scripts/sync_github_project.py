"""Mirror reviewed local tasks to the approved organization Project; dry-run by default."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

from poc_tracker import BASE, LAB, derive, now, write_json

ORG = "AI-SRE-Oberveability"
USER = "javedkumail"
CONFIG = LAB / "tracking/github-project.json"
REPOSITORIES = {
    "infra": "AI-Observability-Infra",
    "workloads": "ai-agent-workloads",
    "observability-config": "ai-observability-config",
    "lab": "ai-observability-lab",
}
START = "<!-- ai-sre-poc-managed:start -->"
END = "<!-- ai-sre-poc-managed:end -->"
PROJECT_QUERY = """query($org:String!,$number:Int!){organization(login:$org){
  projectV2(number:$number){id number title url public
    repositories(first:10){nodes{nameWithOwner}pageInfo{hasNextPage}}
    fields(first:40){nodes{... on ProjectV2FieldCommon{id name dataType}
      ... on ProjectV2SingleSelectField{options{id name}}}}
    views(first:20){nodes{id name layout}}
    items(first:100){nodes{id content{... on Issue{id number url state}}
      fieldValues(first:30){nodes{
        ... on ProjectV2ItemFieldSingleSelectValue{name field{... on ProjectV2FieldCommon{name}}}
        ... on ProjectV2ItemFieldTextValue{text field{... on ProjectV2FieldCommon{name}}}
      }}}pageInfo{hasNextPage}}
  }}}"""


def repository_for(task):
    return REPOSITORIES.get(task["repo"].split("/")[0], REPOSITORIES["lab"])


def board_status(status):
    if status == "done":
        return "Done"
    if status == "in_progress":
        return "In Progress"
    return "Todo"


def observed_fields(item):
    """Unselected metadata union variants can be empty GraphQL objects."""
    return {
        value["field"]["name"]: value.get("name", value.get("text"))
        for value in item["fieldValues"]["nodes"]
        if value.get("field")
    }


def ensure_issue_state(github, path, issue, desired):
    if issue["state"] == desired:
        return
    try:
        github.rest("PATCH", path, {"state": desired})
    except RuntimeError:
        # A Project workflow can reach the desired state before this request.
        if github.rest("GET", path)["state"] != desired:
            raise


def managed_body(task, row):
    evidence = []
    for name in row["evidence"]:
        relative = Path(name).relative_to("ai-observability-lab").as_posix()
        evidence.append(
            f"- [{relative}](https://github.com/{ORG}/ai-observability-lab/blob/main/{relative})"
        )
    return "\n".join(
        [
            f"<!-- ai-sre-poc-task:{task['id']} -->",
            START,
            f"**Task:** {task['id']}  ",
            f"**Phase:** {task['id'].split('.')[0]}  ",
            f"**Responsible:** {task['owner']}  ",
            f"**Evidence status:** {row['status']}  ",
            f"**Dependencies:** {', '.join(task['depends_on']) or 'None'}  ",
            f"**Decision gates:** {', '.join(task['gates']) or 'None'}  ",
            f"**Currently waiting for:** {', '.join(row['blocked_by']) or 'None'}",
            "",
            "### Acceptance",
            "",
            task["acceptance"],
            "",
            "### Evidence",
            "",
            *(evidence or ["No completed-step evidence recorded."]),
            "",
            "Source of truth: [POC tracker](https://github.com/"
            + ORG
            + "/ai-observability-lab/blob/main/POC_TRACKER.md). Drafts and pending decisions do not count as delivery.",
            END,
        ]
    )


def merge_body(previous, managed):
    """Preserve human notes outside the tool's explicitly managed block."""
    if START in previous and END in previous:
        head, rest = previous.split(START, 1)
        _, tail = rest.split(END, 1)
        block = managed.split(START, 1)[1].split(END, 1)[0]
        return head + START + block + END + tail
    if previous.strip():
        raise ValueError("Refusing to replace an issue without a managed block")
    return managed


class GitHub:
    def __init__(self):
        portable = BASE / ".runtime/github-cli/bin/gh.exe"
        executable = shutil.which("gh") or (
            str(portable) if portable.is_file() else None
        )
        if not executable:
            raise RuntimeError(
                "Install GitHub CLI and sign in with the approved project scope"
            )
        env = dict(os.environ)
        isolated = BASE / ".runtime/github-cli-auth"
        if "GH_CONFIG_DIR" not in env and isolated.is_dir():
            env["GH_CONFIG_DIR"] = str(isolated)
        token = subprocess.run(
            [executable, "auth", "token", "--hostname", "github.com"],
            capture_output=True,
            text=True,
            env=env,
            timeout=20,
        )
        if token.returncode or not token.stdout.strip():
            raise RuntimeError("Sign in securely with gh auth login --scopes project")
        self._token = token.stdout.strip()
        self._last_write = 0.0
        if self.rest("GET", "/user")["login"] != USER:
            raise RuntimeError(
                "Authenticated GitHub identity is not the approved personal user"
            )
        member = self.rest("GET", f"/orgs/{ORG}/memberships/{USER}")
        if member["state"] != "active" or member["role"] != "admin":
            raise RuntimeError(
                "Expected active personal ownership of the selected organization"
            )

    def request(self, method, path, body=None, *, mutation=False):
        if not path.startswith("/") or path.startswith("//"):
            raise ValueError("GitHub API path required")
        if mutation:
            time.sleep(max(0, 1.1 - (time.monotonic() - self._last_write)))
            self._last_write = time.monotonic()
        request = urllib.request.Request(
            "https://api.github.com" + path,
            method=method,
            data=json.dumps(body).encode() if body is not None else None,
            headers={
                "Authorization": "Bearer " + self._token,
                "Accept": "application/vnd.github+json",
                "Content-Type": "application/json",
                "User-Agent": "ai-sre-poc-project-sync",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=40) as response:
                content = response.read()
                return json.loads(content) if content else None
        except urllib.error.HTTPError as exc:
            raise RuntimeError(
                f"GitHub HTTP {exc.code} for {path}; token is not logged"
            ) from None

    def rest(self, method, path, body=None):
        return self.request(method, path, body, mutation=method != "GET")

    def gql(self, query, variables=None):
        response = self.request(
            "POST",
            "/graphql",
            {"query": query, "variables": variables or {}},
            mutation=query.lstrip().startswith("mutation"),
        )
        if response.get("errors"):
            raise RuntimeError(
                "GitHub GraphQL: " + "; ".join(e["message"] for e in response["errors"])
            )
        return response["data"]


def project(github, config):
    result = github.gql(PROJECT_QUERY, {"org": ORG, "number": config["project_number"]})
    value = result["organization"]["projectV2"]
    if not value or value["id"] != config["project_id"]:
        raise RuntimeError(
            "Existing approved Project ID does not match; refusing to create a duplicate"
        )
    if value["items"]["pageInfo"]["hasNextPage"]:
        raise RuntimeError(
            "Project exceeds this lab's 100-item bounded sync; add pagination first"
        )
    return value


def configure(github, config, current):
    readme = (
        "# AI SRE Observability POC\n\nShared delivery tracking for the four repositories. "
        "Terraform owns Azure infrastructure; workloads, observability configuration and lab "
        "coordination have separate owners.\n\nLocal tracking/plan.json and tracking/state.json "
        "are the source of truth. Synchronize after each work step with "
        "scripts/sync_github_project.py --apply. Evidence status preserves draft, blocked and "
        "pending-decision details; Done requires local acceptance evidence.\n\n"
        f"[HLD](https://github.com/{ORG}/ai-observability-lab/blob/main/HLD.md) · "
        f"[POC tracker](https://github.com/{ORG}/ai-observability-lab/blob/main/POC_TRACKER.md)"
    )
    github.gql(
        """mutation($input:UpdateProjectV2Input!){updateProjectV2(input:$input){projectV2{id title url}}}""",
        {
            "input": {
                "projectId": current["id"],
                "title": config["project_title"],
                "shortDescription": "Step-by-step AI agents, observability and read-only SRE POC across four repositories.",
                "readme": readme,
            }
        },
    )
    for name in config["repository_names"]:
        repo = github.rest("GET", f"/repos/{ORG}/{name}")
        if repo["owner"]["login"] != ORG or not repo["permissions"]["admin"]:
            raise RuntimeError("Repository owner/admin mismatch")
        github.gql(
            """mutation($input:LinkProjectV2ToRepositoryInput!){linkProjectV2ToRepository(input:$input){clientMutationId}}""",
            {"input": {"projectId": current["id"], "repositoryId": repo["node_id"]}},
        )
    names = {field["name"] for field in current["fields"]["nodes"]}
    for name in ["Task ID", "Phase", "Evidence status", "Dependencies", "Responsible"]:
        if name in names:
            continue
        field = {"projectId": current["id"], "name": name, "dataType": "TEXT"}
        if name == "Phase":
            field["dataType"] = "SINGLE_SELECT"
            field["singleSelectOptions"] = [
                {
                    "name": f"P{i}",
                    "color": color,
                    "description": "POC delivery phase " + str(i),
                }
                for i, color in enumerate(
                    ["GRAY", "BLUE", "PURPLE", "YELLOW", "ORANGE", "PINK", "GREEN"]
                )
            ]
        github.gql(
            """mutation($input:CreateProjectV2FieldInput!){createProjectV2Field(input:$input){projectV2Field{... on ProjectV2FieldCommon{id name}}}}""",
            {"input": field},
        )
    views = current["views"]["nodes"]
    board = next((v for v in views if v["layout"] == "BOARD_LAYOUT"), views[0])
    github.gql(
        """mutation($input:UpdateProjectV2ViewInput!){updateProjectV2View(input:$input){projectV2View{id name layout}}}""",
        {
            "input": {
                "viewId": board["id"],
                "name": "Delivery board",
                "layout": "BOARD_LAYOUT",
            }
        },
    )
    if not any(v["name"] == "All tasks" for v in views):
        github.gql(
            """mutation($input:CreateProjectV2ViewInput!){createProjectV2View(input:$input){projectV2View{id name layout}}}""",
            {
                "input": {
                    "projectId": current["id"],
                    "name": "All tasks",
                    "layout": "TABLE_LAYOUT",
                }
            },
        )


def sync(github, config, plan, state, rows):
    current = project(github, config)
    fields = {field["name"]: field for field in current["fields"]["nodes"]}
    required = {
        "Status",
        "Task ID",
        "Phase",
        "Evidence status",
        "Dependencies",
        "Responsible",
    }
    if required - fields.keys():
        raise RuntimeError("Project needs --setup before task synchronization")
    existing = {}
    for name in config["repository_names"]:
        issues = github.rest(
            "GET", f"/repos/{ORG}/{name}/issues?state=all&per_page=100"
        )
        if len(issues) == 100:
            raise RuntimeError(
                "Issue page reached sync bound; add pagination before continuing"
            )
        for issue in issues:
            match = re.search(
                r"<!-- ai-sre-poc-task:(P\d+\.\d+) -->", issue.get("body") or ""
            )
            if match:
                if match[1] in existing:
                    raise RuntimeError(
                        "Duplicate managed task issue; inspect before continuing"
                    )
                existing[match[1]] = issue
    by_id = {row["id"]: row for row in rows}
    option_ids = {o["name"]: o["id"] for o in fields["Status"]["options"]}
    phase_ids = {o["name"]: o["id"] for o in fields["Phase"]["options"]}
    mapping = config.setdefault("items", {})
    for task in plan["tasks"]:
        row = by_id[task["id"]]
        repo = repository_for(task)
        title = f"[{task['id']}] {task['title']}"
        managed = managed_body(task, row)
        issue = existing.get(task["id"])
        if issue is None:
            issue = github.rest(
                "POST", f"/repos/{ORG}/{repo}/issues", {"title": title, "body": managed}
            )
        else:
            if issue["repository_url"].rsplit("/", 1)[1] != repo:
                raise RuntimeError(
                    "Existing task issue belongs to a different repository; do not silently transfer it"
                )
            body = merge_body(issue.get("body") or "", managed)
            if issue["title"] != title or issue.get("body") != body:
                issue = github.rest(
                    "PATCH",
                    f"/repos/{ORG}/{repo}/issues/{issue['number']}",
                    {"title": title, "body": body},
                )
        old = mapping.get(task["id"], {})
        item_id = old.get("project_item_id")
        if not item_id:
            added = github.gql(
                """mutation($input:AddProjectV2ItemByIdInput!){addProjectV2ItemById(input:$input){item{id}}}""",
                {"input": {"projectId": current["id"], "contentId": issue["node_id"]}},
            )
            item_id = added["addProjectV2ItemById"]["item"]["id"]
        values = {
            "Task ID": {"text": task["id"]},
            "Phase": {"singleSelectOptionId": phase_ids[task["id"].split(".")[0]]},
            "Evidence status": {"text": row["status"]},
            "Dependencies": {"text": ", ".join(task["depends_on"]) or "None"},
            "Responsible": {"text": task["owner"]},
            "Status": {"singleSelectOptionId": option_ids[board_status(row["status"])]},
        }
        if old.get("values") != values or old.get("project_item_id") != item_id:
            variables = {}
            declarations, mutations = [], []
            for index, (name, value) in enumerate(values.items()):
                variable = f"v{index}"
                declarations.append(f"${variable}:UpdateProjectV2ItemFieldValueInput!")
                variables[variable] = {
                    "projectId": current["id"],
                    "itemId": item_id,
                    "fieldId": fields[name]["id"],
                    "value": value,
                }
                mutations.append(
                    f"m{index}:updateProjectV2ItemFieldValue(input:${variable}){{clientMutationId}}"
                )
            github.gql(
                "mutation(" + ",".join(declarations) + "){" + " ".join(mutations) + "}",
                variables,
            )
        desired = "closed" if row["status"] == "done" else "open"
        ensure_issue_state(
            github,
            f"/repos/{ORG}/{repo}/issues/{issue['number']}",
            issue,
            desired,
        )
        mapping[task["id"]] = {
            "repository": repo,
            "issue_number": issue["number"],
            "issue_node_id": issue["node_id"],
            "issue_url": issue["html_url"],
            "project_item_id": item_id,
            "evidence_status": row["status"],
            "values": values,
        }
        config["status"] = "synchronizing"
        write_json(CONFIG, config)
        print(
            f"{task['id']}: {repo}#{issue['number']} -> {board_status(row['status'])}",
            flush=True,
        )
    verified = project(github, config)
    linked = {repo["nameWithOwner"] for repo in verified["repositories"]["nodes"]}
    required_links = {f"{ORG}/{name}" for name in config["repository_names"]}
    if not required_links.issubset(linked):
        raise RuntimeError("Not all four repositories are linked to the shared Project")
    actual = {item["id"]: item for item in verified["items"]["nodes"]}
    for task_id, expected in mapping.items():
        item = actual[expected["project_item_id"]]
        if item["content"]["id"] != expected["issue_node_id"]:
            raise RuntimeError("Project content identity mismatch")
        observed = observed_fields(item)
        if (
            observed.get("Evidence status") != expected["evidence_status"]
            or observed.get("Task ID") != task_id
        ):
            raise RuntimeError("Project task fields did not verify")
        if observed.get("Status") != board_status(expected["evidence_status"]):
            raise RuntimeError("Project board status did not verify")
        for name in ["Dependencies", "Responsible"]:
            if observed.get(name) != expected["values"][name]["text"]:
                raise RuntimeError(f"Project {name} field did not verify")
        if observed.get("Phase") != task_id.split(".")[0]:
            raise RuntimeError("Project phase did not verify")
        expected_state = "CLOSED" if expected["evidence_status"] == "done" else "OPEN"
        if item["content"]["state"] != expected_state:
            raise RuntimeError("Managed issue open/closed state did not verify")
    config.update(
        {
            "status": "ready",
            "verified_at": now(),
            "project_url": verified["url"],
            "task_count": len(plan["tasks"]),
            "visibility": "public" if verified["public"] else "private",
            "views": verified["views"]["nodes"],
        }
    )
    write_json(CONFIG, config)
    report = {
        "organization": ORG,
        "project_url": verified["url"],
        "project_id": verified["id"],
        "verified_at": config["verified_at"],
        "tasks": len(mapping),
        "status_counts": dict(
            Counter(item["evidence_status"] for item in mapping.values())
        ),
        "board_counts": dict(
            Counter(board_status(item["evidence_status"]) for item in mapping.values())
        ),
        "repositories": sorted({item["repository"] for item in mapping.values()}),
        "linked_repositories": sorted(linked),
        "visibility": config["visibility"],
        "views": config["views"],
    }
    write_json(LAB / "evidence/shared-project-verification.json", report)
    print(json.dumps(report, indent=2), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Explicitly update the approved GitHub Project and managed issues",
    )
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Configure the existing Project's name, links, fields and views",
    )
    args = parser.parse_args()
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    if config["organization"] != ORG or set(config["repository_names"]) != set(
        REPOSITORIES.values()
    ):
        raise ValueError(
            "Project sync configuration is outside the approved repository scope"
        )
    plan = json.loads((LAB / "tracking/plan.json").read_text(encoding="utf-8"))
    state = json.loads((LAB / "tracking/state.json").read_text(encoding="utf-8"))
    rows = derive(plan, state, BASE)
    if not args.apply:
        print(
            json.dumps(
                {
                    "mode": "dry-run",
                    "tasks": len(rows),
                    "board_counts": dict(
                        Counter(board_status(row["status"]) for row in rows)
                    ),
                },
                indent=2,
            )
        )
        return
    github = GitHub()
    current = project(github, config)
    if args.setup:
        configure(github, config, current)
    sync(github, config, plan, state, rows)


if __name__ == "__main__":
    main()
