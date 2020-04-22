from typing import Dict, List, Tuple, Union

import pytest

from datastruct import exceptions
from datastruct.ds import INVALID, KeyDefinedValue, convert


@pytest.mark.parametrize(
    "annotation,value", [(float, 8.0), (int, 8), (bool, True), (str, "hello")]
)
def test_basic_types_ok(annotation, value):
    out = convert(annotation, value)
    assert out.flatten() == value
    assert not out.get_errors()


@pytest.mark.parametrize(
    "annotation,value", [(float, 8), (int, 8.0), (bool, "bla"), (str, True)]
)
def test_basic_types_not_ok(annotation, value):
    out = convert(annotation, value)
    assert out.flatten() == INVALID
    assert out.get_errors()
    assert isinstance(out.get_errors()[0], exceptions.WrongTypeError)


@pytest.mark.parametrize(
    "annotation,value",
    [
        (List[int], [8,]),  # noqa E231
        (Tuple[int], (8,)),
        (Union[int, float], 8),
        (Dict[int, int], {1: 2}),
    ],
)
def test_qualified_generic_ok(annotation, value):
    out = convert(annotation, value)
    assert out.flatten() == value
    assert not out.get_errors()


@pytest.mark.parametrize(
    "annotation,value",
    [
        (List[int], [8.0,]),  # noqa E231
        (List[int], (8,)),
        (Union[int, float], "hello"),
        (Dict[float, int], {1: 2}),
        (Dict[int, float], {1: 2}),
    ],
)
def test_qualified_generic_not_ok(annotation, value):
    out = convert(annotation, value)
    assert out.flatten() != value
    assert out.get_errors()


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
    o = convert(annotation, value)
    assert not o.get_errors()
    assert o.value == expected


@pytest.mark.parametrize(
    "annotation,value,errs",
    [
        (Example, dict(a=1.0), (exceptions.WrongTypeError(1.0, int),),),
        (Example, dict(b=True), (exceptions.WrongTypeError(True, str),),),
        (Example, dict(c=2), (exceptions.WrongTypeError(2, float),),),
        (
            Example,
            dict(z=2),
            (exceptions.WrongValueError("z", "key in ('a', 'b', 'c')"),),
        ),
    ],
)
def test_kdv_not_ok(annotation, value, errs):
    o = convert(annotation, value)
    assert o.get_errors() == errs
    assert o.value == INVALID
