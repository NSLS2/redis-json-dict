from __future__ import annotations

import contextlib
import subprocess
import time as ttime
import uuid

import pytest
import redis

from redis_json_dict import RedisJSONDict


@contextlib.contextmanager
def redis_startup():
    try:
        ps = subprocess.Popen(
            [
                "redis-server",
            ],
        )
        ttime.sleep(1.3)  # make sure the process is started
        yield ps
    finally:
        ps.terminate()
        redis_client = redis.Redis(host="localhost", port=6379)
        redis_client.shutdown()


@pytest.fixture(scope="session")
def redis_server():  # noqa: PT004
    with redis_startup() as redis_fixture:  # noqa: F841
        yield


@pytest.fixture()
def d():
    redis_client = redis.Redis(host="localhost", port=6379)
    prefix = uuid.uuid4().hex
    yield RedisJSONDict(redis_client, prefix=prefix)
    # Clean up.
    keys = list(redis_client.scan_iter(match=f"{prefix}*"))
    if keys:
        redis_client.delete(*keys)
