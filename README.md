# kubescout-mcp

A read-only Kubernetes MCP server for Claude Code, built with FastMCP in Python.

<!-- Demo: add a GIF here (under 20 seconds) showing Claude Code diagnosing a failing pod
     with kubescout-mcp, from the question to the root cause. -->

## Quick start

Install:

```bash
git clone <this-repo-url> kubescout-mcp && cd kubescout-mcp
python3 -m venv .venv
.venv/bin/pip install -e .
```

Add it to Claude Code:

```bash
claude mcp add --scope user kubescout-mcp -- $(pwd)/.venv/bin/kubescout-mcp
claude mcp list
```

The list should show `kubescout-mcp ... Connected`. Restart your Claude Code session, then try:

```text
List all pods in every namespace and tell me which ones are not ready.
```

## Why this exists

Checking a cluster from an AI assistant usually means pasting `kubectl` output by hand.
This server gives Claude Code direct, read-only access to your cluster, so it can look up pods,
logs and events by itself. It cannot change anything, so it is safe to point at a real cluster.

## Features

- Lists namespaces, nodes, pods, deployments and services.
- Reads pod logs, with an optional container and a line limit (1 to 1000).
- Shows recent namespace events to help debug failing pods.
- Returns compact JSON (readiness, restarts, replicas, images) instead of full API objects.
- Uses your current kubeconfig context, and falls back to in-cluster config.
- Includes a small demo cluster setup (k3d, SQLite and nginx) to try the tools on.

## Tools

| Tool | Purpose | Mode |
|------|---------|------|
| `list_namespaces` | All namespaces with status and creation time | read-only |
| `list_nodes` | Nodes with readiness, kubelet version, OS image, CPU and memory | read-only |
| `list_pods` | Pods with phase, ready count, restarts, node and IP | read-only |
| `list_deployments` | Deployments with desired, ready and available replicas, and images | read-only |
| `list_services` | Services with type, cluster IP and ports | read-only |
| `get_pod_logs` | Last N log lines of a pod or one of its containers | read-only |
| `list_events` | Recent events in a namespace, newest last | read-only |

`list_pods`, `list_deployments` and `list_services` take `namespace` (default `default`) and
`all_namespaces` (default `false`). `list_events` takes `namespace` and `limit` (default 50).
`get_pod_logs` takes `pod`, `namespace`, `container` and `tail_lines` (default 100).

## Example prompts

| Prompt | Expected result |
|--------|-----------------|
| "Which pods are not ready in all namespaces?" | A list of pods with their ready count and phase. |
| "Show the last 50 log lines of the web pod." | The recent log output of that pod. |
| "Why is my deployment not rolling out?" | Deployment replica counts plus recent events for the namespace. |
| "What nodes do I have and are they healthy?" | Each node with Ready status, version and capacity. |

## Security model

- Every tool is read-only. The server has no create, update, delete or exec tools.
- It never runs shell commands and never calls `kubectl`. It talks to the API server through the
  official Python `kubernetes` client.
- Credentials: it loads your kubeconfig (`~/.kube/config` or the file in `KUBECONFIG`) with your
  current context, so it can see what your user can see. If no kubeconfig is found, it tries
  in-cluster config. Secrets are not exposed by any tool, and the secrets API is never called.
- There is no write mode and no allowlist yet. For stricter access, use a kubeconfig whose user
  has a read-only RBAC role.
- Pod logs can contain sensitive data and attacker-controlled text, so the tool sanitizes and truncates log excerpts before passing them to the model.

## Configuration

| Setting | Description |
|---------|-------------|
| `KUBECONFIG` | Path to the kubeconfig file. Standard Kubernetes behavior, default `~/.kube/config`. |
| kubeconfig current context | Decides which cluster is used. Switch with `kubectl config use-context`. |

The server has no flags or other environment variables.

## Try it with the demo cluster

The sibling project `test-kuber` creates a k3s cluster in Docker (via k3d) with two pods: a SQLite
database served by Datasette, and an nginx page that shows its data. It is a handy target for
these tools.

```bash
cd ../test-kuber
make setup   # installs k3d and kubectl to ~/.local/bin, once
make up      # creates the cluster and deploys both pods, then open http://localhost:8080
make down    # deletes the cluster
```

## Development

```bash
.venv/bin/pip install -e ".[dev]"
.venv/bin/pytest
```

The tests cover the formatters in `src/kubescout_mcp/formatters.py`. The tools themselves were checked
by hand against a k3d cluster.

Layout:

- `src/kubescout_mcp/server.py`: FastMCP server and tool definitions.
- `src/kubescout_mcp/k8s.py`: lazy kubeconfig loading and API clients.
- `src/kubescout_mcp/formatters.py`: turns API objects into small dicts.

## Roadmap

These items are planned, not built yet.

- Describe a single pod or deployment.
- List ConfigMaps, ingresses and persistent volume claims.
- Choose the kubeconfig context per call.
- Opt-in write actions (for example scale a deployment) behind an explicit flag and an allowlist.
- Automated tests for the tools and a CI workflow.

## Contributing

Issues and pull requests are welcome. Keep tools read-only by default, add a test for any new
formatter, and run `pytest` before you open a pull request.

## License

No license file has been added yet.
