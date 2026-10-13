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


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
