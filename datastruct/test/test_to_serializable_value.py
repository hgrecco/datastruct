from typing import Dict, List, Tuple

import pytest

from datastruct.ds import KeyDefinedValue, from_plain_value, to_plain_value


@pytest.mark.parametrize(
    "annotation,value", [(float, 8.0), (int, 8), (bool, True), (str, "hello")]
)
def test_basic_types_ok(annotation, value):
    out = from_plain_value(annotation, value)
    assert not out.get_errors()
    assert value == to_plain_value(annotation, out.flatten())


@pytest.mark.parametrize(
    "annotation,value",
    [
        (List[int], [8,]),  # noqa E231
        (Tuple[int], (8,)),
        # (Union[int, float], 8),
        (Dict[int, int], {1: 2}),
    ],
)
def test_qualified_generic_ok(annotation, value):
    out = from_plain_value(annotation, value)
    assert not out.get_errors()
    assert value == to_plain_value(annotation, out.flatten())


class Example(KeyDefinedValue):

    content = {"a": int, "b": str, "c": float}


@pytest.mark.parametrize(
    "annotation,value,expected",
    [
        (Example, dict(a=1), 1),
        (Example, dict(b="s"), "s"),
        (Example, dict(c=2.0), 2.0),
    ],
)
def test_kdv_ok(annotation, value, expected):
    out = from_plain_value(annotation, value)
    assert not out.get_errors()
    assert value == to_plain_value(annotation, out.flatten())
