"""Convert Kubernetes API objects into small JSON-friendly dicts."""


def _ts(value):
    return value.isoformat() if value else None


def namespace(ns) -> dict:
    return {
        "name": ns.metadata.name,
        "status": ns.status.phase,
        "created": _ts(ns.metadata.creation_timestamp),
    }


def pod(p) -> dict:
    statuses = p.status.container_statuses or []
    return {
        "name": p.metadata.name,
        "namespace": p.metadata.namespace,
        "phase": p.status.phase,
        "ready": f"{sum(1 for c in statuses if c.ready)}/{len(p.spec.containers)}",
        "restarts": sum(c.restart_count for c in statuses),
        "node": p.spec.node_name,
        "ip": p.status.pod_ip,
        "created": _ts(p.metadata.creation_timestamp),
    }


def deployment(d) -> dict:
    return {
        "name": d.metadata.name,
        "namespace": d.metadata.namespace,
        "replicas": d.spec.replicas,
        "ready": d.status.ready_replicas or 0,
        "available": d.status.available_replicas or 0,
        "images": [c.image for c in d.spec.template.spec.containers],
    }


def service(s) -> dict:
    return {
        "name": s.metadata.name,
        "namespace": s.metadata.namespace,
        "type": s.spec.type,
        "cluster_ip": s.spec.cluster_ip,
        "ports": [f"{p.port}/{p.protocol}" for p in s.spec.ports or []],
    }


def node(n) -> dict:
    ready = next((c.status for c in n.status.conditions if c.type == "Ready"), "Unknown")
    return {
        "name": n.metadata.name,
        "ready": ready,
        "kubelet_version": n.status.node_info.kubelet_version,
        "os_image": n.status.node_info.os_image,
        "cpu": n.status.capacity.get("cpu"),
        "memory": n.status.capacity.get("memory"),
    }


def event(e) -> dict:
    return {
        "type": e.type,
        "reason": e.reason,
        "object": f"{e.involved_object.kind}/{e.involved_object.name}",
        "message": e.message,
        "count": e.count,
        "last_seen": _ts(e.last_timestamp or e.event_time),
    }
