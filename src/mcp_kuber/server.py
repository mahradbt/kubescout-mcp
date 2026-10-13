"""Read-only Kubernetes MCP server."""
from fastmcp import FastMCP

from . import formatters as fmt
from . import k8s

mcp = FastMCP(
    "mcp-kuber",
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


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
