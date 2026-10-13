from datetime import datetime, timezone
from types import SimpleNamespace as NS

from kubescout_mcp import formatters as fmt

TS = datetime(2026, 1, 1, tzinfo=timezone.utc)


def test_namespace():
    ns = NS(metadata=NS(name="default", creation_timestamp=TS), status=NS(phase="Active"))
    assert fmt.namespace(ns) == {"name": "default", "status": "Active", "created": TS.isoformat()}


def test_pod_ready_and_restarts():
    p = NS(
        metadata=NS(name="a", namespace="ns", creation_timestamp=TS),
        spec=NS(containers=[object(), object()], node_name="n1"),
        status=NS(
            phase="Running",
            pod_ip="1.2.3.4",
            container_statuses=[NS(ready=True, restart_count=1), NS(ready=False, restart_count=2)],
        ),
    )
    out = fmt.pod(p)
    assert out["ready"] == "1/2"
    assert out["restarts"] == 3


def test_pod_without_statuses():
    p = NS(
        metadata=NS(name="a", namespace="ns", creation_timestamp=None),
        spec=NS(containers=[object()], node_name=None),
        status=NS(phase="Pending", pod_ip=None, container_statuses=None),
    )
    out = fmt.pod(p)
    assert out["ready"] == "0/1" and out["created"] is None


def test_deployment_defaults_ready_to_zero():
    d = NS(
        metadata=NS(name="d", namespace="ns"),
        spec=NS(replicas=2, template=NS(spec=NS(containers=[NS(image="nginx")]))),
        status=NS(ready_replicas=None, available_replicas=None),
    )
    assert fmt.deployment(d)["ready"] == 0
    assert fmt.deployment(d)["images"] == ["nginx"]


def test_service_ports():
    s = NS(
        metadata=NS(name="s", namespace="ns"),
        spec=NS(type="ClusterIP", cluster_ip="10.0.0.1", ports=[NS(port=80, protocol="TCP")]),
    )
    assert fmt.service(s)["ports"] == ["80/TCP"]
