from __future__ import annotations

import copy

import pytest

from redis_json_dict import ObservableMapping, ObservableSequence

# ruff: noqa: ARG001


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("integer", 1),
        ("float", 2.0),
        ("array", ["a", 2, 3.0]),
        ("object", {"A": "a", "B": 2, "C": 3.0}),
    ],
)
def test_round_trip(redis_server, d, key, value):
    d[key] = value
    assert d[key] == value
    assert len(d) == 1
    assert list(d) == [key]


def test_missing(redis_server, d):
    d["a"] = 1
    with pytest.raises(KeyError):
        d["does not exist"]
    assert d.get("does not exist") is None
    assert d.get("does not exist", "default") == "default"


def test_iteration(redis_server, d):
    d["a"] = 1
    d["b"] = 2
    # Unlike Python dict this does not guarantee that iteration order is
    # stable.
    assert sorted(d.keys()) == ["a", "b"]
    assert sorted(d.values()) == [1, 2]
    assert sorted(d.items()) == [("a", 1), ("b", 2)]


def test_contains(redis_server, d):
    d["a"] = 1
    assert "a" in d
    assert "b" not in d


def test_update(redis_server, d):
    d["unchanged"] = 0
    d["altered"] = 1
    d.update({"altered": 2, "added": 3})
    assert dict(d) == {"unchanged": 0, "altered": 2, "added": 3}


def test_setdefault(redis_server, d):
    d["unchanged"] = 0
    d.setdefault("unchanged", 1)  # should have no effect
    assert d["unchanged"] == 0
    d.setdefault("added", 1)
    assert d["added"] == 1


def test_pop(redis_server, d):
    d["a"] = 1
    d.pop("a")
    assert len(d) == 0
    assert "a" not in d
    with pytest.raises(KeyError):
        d.pop("a")
    d.pop("a", None)


def test_popitem(redis_server, d):
    d["a"] = 1
    item = d.popitem()
    assert item == ("a", 1)
    with pytest.raises(KeyError):
        d.popitem()


def test_clear(redis_server, d):
    d.update({"a": 1, "b": 2})
    d.clear()
    assert len(d) == 0
    assert dict(d) == {}


def test_mutation(redis_server, d):
    # dict
    d["x"] = [1, 2]
    d["x"].append(3)
    assert d["x"] == [1, 2, 3]
    d["x"].remove(1)
    assert d["x"] == [2, 3]
    d["x"].insert(1, 0)
    assert d["x"] == [2, 0, 3]

    # list
    d["y"] = {"a": 1, "b": 2}
    d["y"]["c"] = 3
    assert d["y"] == {"a": 1, "b": 2, "c": 3}
    d["y"].pop("a")
    assert d["y"] == {"b": 2, "c": 3}


def test_nested_mutation(redis_server, d):
    # Mutable lists and dicts and dicts in lists
    d["x"] = {}
    d["x"]["y"] = {}
    d["x"]["y"]["z"] = {}
    d["x"]["y"]["z"]["i"] = []
    d["x"]["y"]["z"]["i"].append(1)
    d["x"]["y"]["z"]["j"] = 2
    d["x"]["y"]["z"]["k"] = []
    d["x"]["y"]["z"]["k"].append({})
    d["x"]["y"]["z"]["k"][0]["p"] = []
    d["x"]["y"]["z"]["k"][0]["p"].append(3)

    assert d == {"x": {"y": {"z": {"i": [1], "j": 2, "k": [{"p": [3]}]}}}}


def test_copy_returns_plain_object(redis_server, d):
    d["x"] = {}
    d["y"] = []
    assert isinstance(d["x"], ObservableMapping)
    assert isinstance(d["y"], ObservableSequence)
    c = copy.deepcopy(d)
    assert isinstance(c["x"], dict)
    assert isinstance(c["y"], list)
