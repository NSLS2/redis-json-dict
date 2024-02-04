# redis-dict-json

## Usage

```py
>>> import redis
>>> redis_client = redis.Redis('localhost', 6379)
>>> d = RedisJSONDict(redis_client, prefix='my_dict')
>>> d
{}
```

All user modifications, including mutation of nested lists or dicts, are
immediately synchronized to the Redis server.

## Design Requirements

- The dictionary implements Python's `collections.abc.MutableMapping` interface.
- All values stored in Redis are JSON-encoded, readily inspected with developer
  eyeballs and possible to operate on from clients in languages other than
  Python.
- Keys may be prefixed to reduce the likelihood of collisions when one Redis
  is shared by multiple applications.
- No data is cached locally, so it is impossible to obtain a stale result.
  However, the dictionary may be _composed_ with other libraries, such as
  `cachetools`, to implement TTL caching for example.
- Top-level items like `d['sample']` may be accessed without synchronizing
  the entire dictionary. Nested objects like `d['sample']['color']` are
  supported (but may be less efficient).
- Mutating nested items, with operations like `d['sample']['color'] = 'red'` or
  `d['sample']['positions'].append(3)` triggers synchronization.
