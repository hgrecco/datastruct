import pytest

from datastruct.common import merge, merge_two


@pytest.mark.parametrize(
    "dcts,out",
    [
        (
            [{1: {"a": "A"}, 2: {"b": "B"}}, {2: {"c": "C"}, 3: {"d": "D"}}],
            {1: {"a": "A"}, 2: {"b": "B", "c": "C"}, 3: {"d": "D"}},
        ),
        (
            [{1: {"a": "A"}, 2: {"b": "B"}}, {2: {"b": "E"}, 3: {"d": "D"}}],
            {1: {"a": "A"}, 2: {"b": "B"}, 3: {"d": "D"}},
        ),
    ],
)
def test_merge_two(dcts, out):
    assert merge_two(dcts[0], dcts[1]) == out
    assert merge(dcts) == out


@pytest.mark.parametrize(
    "dcts,out",
    [
        (
            [{1: {"a": "A"}, 2: {"b": "B"}}, {2: {"c": "C"}, 3: {"d": "D"}}],
            {1: {"a": "A"}, 2: {"b": "B", "c": "C"}, 3: {"d": "D"}},
        ),
        (
            [{1: {"a": "A"}, 2: {"b": "B"}}, {2: {"b": "E"}, 3: {"d": "D"}}],
            {1: {"a": "A"}, 2: {"b": "B"}, 3: {"d": "D"}},
        ),
    ],
)
def test_merge_two_raise(dcts, out):
    try:
        assert merge_two(dcts[0], dcts[1], raise_on_conflict=True)
        assert False
    except:  # noqa: E722
        assert True

    try:
        assert merge(dcts, raise_on_conflict=True)
        assert False
    except:  # noqa: E722
        assert True
