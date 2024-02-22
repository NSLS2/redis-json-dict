from __future__ import annotations

import uuid

import pytest
import redis

from redis_json_dict import RedisJSONDict


@pytest.fixture()
def d():
    redis_client = redis.Redis(host="localhost", port=6379)
    redis_client.flushall()
    prefix = uuid.uuid4().hex
    yield RedisJSONDict(redis_client, prefix=prefix)
    # Clean up.
    keys = list(redis_client.scan_iter(match=f"{prefix}*"))
    if keys:
        redis_client.delete(*keys)
