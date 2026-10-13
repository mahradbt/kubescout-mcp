"""Thin wrapper around the kubernetes client: lazy config loading."""
from functools import lru_cache

from kubernetes import client, config


@lru_cache(maxsize=1)
def _load() -> None:
    try:
        config.load_kube_config()
    except config.ConfigException:
        config.load_incluster_config()


def core() -> client.CoreV1Api:
    _load()
    return client.CoreV1Api()


def apps() -> client.AppsV1Api:
    _load()
    return client.AppsV1Api()
