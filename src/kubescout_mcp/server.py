"""Read-only Kubernetes MCP server."""
from fastmcp import FastMCP

from . import formatters as fmt
from . import k8s

mcp = FastMCP(
    "kubescout-mcp",
    instructions="Read-only tools to inspect a Kubernetes cluster (nodes, namespaces, workloads, logs, events).",
)


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
    """Return the last `tail_lines` log lines of a pod (optionally a specific container)."""
    return k8s.core().read_namespaced_pod_log(
        pod, namespace, container=container, tail_lines=min(max(tail_lines, 1), 1000)
    )


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
