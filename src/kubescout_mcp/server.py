"""Read-only Kubernetes MCP server."""
import re

from fastmcp import FastMCP

from . import formatters as fmt
from . import k8s

mcp = FastMCP(
    "kubescout-mcp",
    instructions="Read-only tools to inspect a Kubernetes cluster (nodes, namespaces, workloads, logs, events).",
)


def _sanitize_untrusted_log_output(logs: str, max_chars: int = 20000) -> str:
    """Return a redacted, bounded log excerpt for model context.

    Pod logs are attacker-controlled input and must be treated as untrusted. We strip ANSI
    control codes, redact common secret-bearing values, and cap the output size before handing it
    to the model.
    """
    if not logs:
        return "No log output available."

    cleaned = re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", logs)
    cleaned = cleaned.replace("\r\n", "\n")

    redactions = [
        (r"(?i)(authorization\s*:\s*bearer\s+)[A-Za-z0-9._~+/=-]+", r"\1[REDACTED]"),
        (r"(?i)(bearer\s+[A-Za-z0-9._~+/=-]{20,})", "[REDACTED]"),
        (r"(?i)(password\s*[:=]\s*)(?:'\")[^'\"]+(?:'\")?", r"\1[REDACTED]"),
        (r"(?i)(token\s*[:=]\s*)(?:'\")[^'\"]+(?:'\")?", r"\1[REDACTED]"),
        (r"(?i)(secret\s*[:=]\s*)(?:'\")[^'\"]+(?:'\")?", r"\1[REDACTED]"),
        (r"(?i)(api[_-]?key\s*[:=]\s*)(?:'\")[^'\"]+(?:'\")?", r"\1[REDACTED]"),
        (r"(?i)(aws_access_key_id\s*[:=]\s*)[A-Za-z0-9]+", r"\1[REDACTED]"),
        (r"(?i)(aws_secret_access_key\s*[:=]\s*)[A-Za-z0-9/+=]+", r"\1[REDACTED]"),
    ]
    for pattern, replacement in redactions:
        cleaned = re.sub(pattern, replacement, cleaned)

    if len(cleaned) > max_chars:
        cleaned = f"{cleaned[:max_chars].rstrip()}\n\n[truncated to {max_chars} characters]"

    return "Untrusted log excerpt (sensitive values redacted):\n" + cleaned


@mcp.tool
def list_namespaces() -> list[dict]:
    """List all namespaces in the cluster."""
    return [fmt.namespace(n) for n in k8s.core().list_namespace().items]


@mcp.tool
def list_nodes() -> list[dict]:
    """List cluster nodes with readiness, version and capacity."""
    return [fmt.node(n) for n in k8s.core().list_node().items]


@mcp.tool
def list_pods(namespace: str = "default", all_namespaces: bool = False) -> list[dict]:
    """List pods with phase, readiness and restart counts."""
    api = k8s.core()
    pods = api.list_pod_for_all_namespaces() if all_namespaces else api.list_namespaced_pod(namespace)
    return [fmt.pod(p) for p in pods.items]


@mcp.tool
def list_deployments(namespace: str = "default", all_namespaces: bool = False) -> list[dict]:
    """List deployments with replica counts and images."""
    api = k8s.apps()
    deps = (
        api.list_deployment_for_all_namespaces()
        if all_namespaces
        else api.list_namespaced_deployment(namespace)
    )
    return [fmt.deployment(d) for d in deps.items]


@mcp.tool
def list_services(namespace: str = "default", all_namespaces: bool = False) -> list[dict]:
    """List services with type, cluster IP and ports."""
    api = k8s.core()
    svcs = api.list_service_for_all_namespaces() if all_namespaces else api.list_namespaced_service(namespace)
    return [fmt.service(s) for s in svcs.items]


@mcp.tool
def get_pod_logs(pod: str, namespace: str = "default", container: str | None = None, tail_lines: int = 100) -> str:
    """Return a redacted, bounded log excerpt for a pod or its container."""
    raw_logs = k8s.core().read_namespaced_pod_log(
        pod, namespace, container=container, tail_lines=min(max(tail_lines, 1), 1000)
    )
    return _sanitize_untrusted_log_output(raw_logs)


@mcp.tool
def list_events(namespace: str = "default", limit: int = 50) -> list[dict]:
    """List recent events in a namespace, newest last. Useful for debugging failing pods."""
    events = k8s.core().list_namespaced_event(namespace).items
    events.sort(key=lambda e: e.last_timestamp or e.event_time or e.metadata.creation_timestamp)
    return [fmt.event(e) for e in events[-limit:]]


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
