from __future__ import annotations

import collections.abc
import copy

import orjson


class RedisJSONDict(collections.abc.MutableMapping):
    """
    A JSON-encodable dict synced to Redis

    >>> import redis
    >>> redis_client = redis.Redis('localhost', 6379)
    >>> d = RedisJSONDict(redis_client, prefix='my_dict')
    """

    def __init__(
        self,
        redis_client,
        prefix,
    ):
        self._redis_client = redis_client
        self._prefix = prefix

    def __repr__(self):
        return repr(dict(self))

    def __iter__(self):
        prefix_len = len(self._prefix)
        yield from (
            key[prefix_len:].decode()  # slice off prefix and decode to str
            # SCAN for all keys matching the prefix.
            # Note that, unlike KEYS, this is incremental/non-blocking.
            for key in self._redis_client.scan_iter(match=f"{self._prefix}*")
        )

    def __len__(self):
        return len(list(iter(self)))

    def __getitem__(self, key):
        # GET and JSON-decode one key.
        json = self._redis_client.get(f"{self._prefix}{key}")
        if json is None:
            raise KeyError(key)
        value = orjson.loads(json)

        # When any nested objects or arrays are mutated, sync
        # the full contents of this top-level value.

        def sync():
            self[key] = observed

        observed = observe(value, sync)
        return observed  # noqa: RET504

    def __setitem__(self, key, value):
        # SET one JSON-encoded value to a key.
        json = orjson.dumps(value, default=_json_encoder_default)
        self._redis_client.set(f"{self._prefix}{key}", json)

    def __delitem__(self, key):
        # DELETE one key.
        self._redis_client.delete(f"{self._prefix}{key}")

    def clear(self):
        # Batch (a performance optimization over default behavior)
        keys = list(self)
        if keys:
            self._redis_client.delete(*(f"{self._prefix}{key}" for key in keys))

    def update(self, d):
        # Batch (a performance optimization over default behavior)
        pipe = self._redis_client.pipeline()
        for key, value in d.items():
            json = orjson.dumps(value, default=_json_encoder_default)
            pipe.set(f"{self._prefix}{key}", json)
        pipe.execute()

    def __copy__(self):
        return dict(self)

    def __deepcopy__(self, memo):
        return copy.deepcopy(dict(self), memo)


class ObservableMapping(collections.abc.MutableMapping):
    def __init__(self, mapping, on_changed):
        self._mapping = mapping
        self._on_changed = on_changed

    def __repr__(self):
        return repr(self._mapping)

    def __iter__(self):
        return iter(self._mapping)

    def __len__(self):
        return len(self._mapping)

    def __getitem__(self, key):
        return self._mapping[key]

    def __setitem__(self, key, value):
        self._mapping[key] = value
        self._on_changed()

    def __delitem__(self, key):
        del self._mapping[key]
        self._on_changed()

    def __eq__(self, other):
        return self._mapping == other

    def __copy__(self):
        return copy.copy(self._mapping)

    def __deepcopy__(self, memo):
        return copy.deepcopy(self._mapping, memo)


class ObservableSequence(collections.abc.MutableSequence):
    def __init__(self, sequence, on_changed):
        self._sequence = list(sequence)
        self._on_changed = on_changed

    def __repr__(self):
        return repr(self._sequence)

    def __iter__(self):
        return iter(self._sequence)

    def __len__(self):
        return len(self._sequence)

    def __getitem__(self, index):
        return self._sequence[index]

    def __setitem__(self, index, value):
        self._sequence[index] = value
        self._on_changed()

    def insert(self, index, value):
        self._sequence.insert(index, value)
        self._on_changed()

    def __delitem__(self, index):
        del self._sequence[index]
        self._on_changed()

    def __add__(self, other):
        return type(self)(self._sequence + other)

    def __eq__(self, other):
        return self._sequence == other

    def __copy__(self):
        return copy.copy(self._sequence)

    def __deepcopy__(self, memo):
        return copy.deepcopy(self._sequence, memo)


def observe(value, on_changed):
    "If value is a collection, return a recursively observable copy."
    if isinstance(value, collections.abc.Mapping):
        result = ObservableMapping(
            {k: observe(v, on_changed) for k, v in value.items()},
            on_changed,
        )
    elif isinstance(value, collections.abc.Sequence) and not isinstance(value, str):
        result = ObservableSequence(
            [observe(item, on_changed) for item in value],
            on_changed,
        )
    else:
        result = value
    return result


def _json_encoder_default(content):
    if isinstance(content, ObservableMapping):
        return content._mapping  # using internal structure for perf
    if isinstance(content, ObservableSequence):
        return content._sequence  # using internal structure for perf
    raise TypeError
