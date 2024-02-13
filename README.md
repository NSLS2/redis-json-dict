# redis-json-dict

[![Actions Status][actions-badge]][actions-link]
[![Documentation Status][rtd-badge]][rtd-link]

[![PyPI version][pypi-version]][pypi-link]
[![Conda-Forge][conda-badge]][conda-link]
[![PyPI platforms][pypi-platforms]][pypi-link]

[![GitHub Discussion][github-discussions-badge]][github-discussions-link]

<!-- SPHINX-START -->

## Usage

```pycon
>>> import redis
... redis_client = redis.Redis("localhost", 6379)
... d = RedisJSONDict(redis_client, prefix="my_dict")
... d
{}
```

All user modifications, including mutation of nested lists or dicts, are
immediately synchronized to the Redis server.

## Design Requirements

- The dictionary implements Python's `collections.abc.MutableMapping` interface.
- All values stored in Redis are JSON-encoded, readily inspected with developer
  eyeballs and possible to operate on from clients in languages other than
  Python.
- Keys may be prefixed to reduce the likelihood of collisions when one Redis is
  shared by multiple applications.
- No data is cached locally, so it is impossible to obtain a stale result.
  However, the dictionary may be _composed_ with other libraries, such as
  `cachetools`, to implement TTL caching for example.
- Top-level items like `d['sample']` may be accessed without synchronizing the
  entire dictionary. Nested objects like `d['sample']['color']` are supported
  (but may be less efficient).
- Mutating nested items, with operations like `d['sample']['color'] = 'red'` or
  `d['sample']['positions'].append(3)` triggers synchronization.

<!-- prettier-ignore-start -->
[actions-badge]:            https://github.com/NSLS2/redis-json-dict/workflows/CI/badge.svg
[actions-link]:             https://github.com/NSLS2/redis-json-dict/actions
[conda-badge]:              https://img.shields.io/conda/vn/conda-forge/redis-json-dict
[conda-link]:               https://github.com/conda-forge/redis-json-dict-feedstock
[github-discussions-badge]: https://img.shields.io/static/v1?label=Discussions&message=Ask&color=blue&logo=github
[github-discussions-link]:  https://github.com/NSLS2/redis-json-dict/discussions
[pypi-link]:                https://pypi.org/project/redis-json-dict/
[pypi-platforms]:           https://img.shields.io/pypi/pyversions/redis-json-dict
[pypi-version]:             https://img.shields.io/pypi/v/redis-json-dict
[rtd-badge]:                https://readthedocs.org/projects/redis-json-dict/badge/?version=latest
[rtd-link]:                 https://redis-json-dict.readthedocs.io/en/latest/?badge=latest

<!-- prettier-ignore-end -->
