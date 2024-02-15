from __future__ import annotations

import importlib.metadata

import redis_json_dict as m


def test_version():
    assert importlib.metadata.version("redis_json_dict") == m.__version__
