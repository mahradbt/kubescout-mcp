# mcp-kuber

A small, read-only [FastMCP](https://github.com/PrefectHQ/fastmcp) server that lets Claude Code
(or any MCP client) inspect a Kubernetes cluster.

## Tools

| Tool | Description |
|------|-------------|
| `list_namespaces` | All namespaces |
| `list_nodes` | Nodes with readiness, version, capacity |
| `list_pods` | Pods with phase, readiness, restarts |
| `list_deployments` | Deployments with replicas and images |
| `list_services` | Services with type, cluster IP, ports |
| `get_pod_logs` | Last N log lines of a pod/container |
| `list_events` | Recent events in a namespace |

Namespaced tools take `namespace` (default `default`) and, where relevant, `all_namespaces`.
The server only reads; it never creates, changes or deletes anything.

## Install

    python3 -m venv .venv
    .venv/bin/pip install -e ".[dev]"
    .venv/bin/pytest

It uses your current kubeconfig context (`~/.kube/config`), falling back to in-cluster config.

## Connect to Claude Code

    claude mcp add --scope user mcp-kuber -- $(pwd)/.venv/bin/mcp-kuber
    claude mcp list        # mcp-kuber ... Connected

Then ask Claude Code things like "list all pods in every namespace" or "show the last logs of the web pod".

## Try it with the demo cluster

The sibling `test-kuber` project creates a k3d cluster with a SQLite (Datasette) pod and an nginx pod
that are handy for testing these tools.
