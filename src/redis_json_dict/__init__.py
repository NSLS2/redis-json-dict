"""
Copyright (c) 2024 Brookhaven National Laboratory. All rights reserved.

redis-json-dict: A Redis-backed persistent Python dictionary
"""

from __future__ import annotations

from ._version import version as __version__

__all__ = ["__version__"]

from redis_json_dict.redis_json_dict import (  # noqa: F401
    ObservableMapping,
    ObservableSequence,
    RedisJSONDict,
)
