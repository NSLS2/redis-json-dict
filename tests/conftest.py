from __future__ import annotations

import os
import uuid

import pytest
import redis

from redis_json_dict import RedisJSONDict


@pytest.fixture()
def d():
    redis_client = redis.Redis(
        host=os.environ.get("TEST_REDIS_HOST", "localhost"),
        port=os.environ.get("TEST_REDIS_PORT", 63798),
    )  # use a different port than usual because are clearing it!
    if os.environ.get("CLEAR_REDIS", "false") == "true":
        redis_client.flushall()
    prefix = uuid.uuid4().hex
    yield RedisJSONDict(redis_client, prefix=prefix)
    # Clean up.
    keys = list(redis_client.scan_iter(match=f"{prefix}*"))
    if keys:
        redis_client.delete(*keys)
