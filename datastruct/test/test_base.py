from typing import Dict, List, Tuple

from datastruct import DataStruct, exceptions


class Example(DataStruct):
    a: int
    b: str
    c: float
    d: bool


class ExampleWithDefault(DataStruct):
    a: int
    b: str = "h"


class ExampleSingle(DataStruct):
    a: int


class ExampleNested(DataStruct):

    a: int
    n: ExampleSingle


class ExampleNestedList(DataStruct):

    a: int
    n: List[ExampleSingle]


class ExampleNestedTuple(DataStruct):

    a: int
    n: Tuple[ExampleSingle]


class ExampleNestedDict(DataStruct):

    a: int
    n: Dict[str, ExampleSingle]


def test_simple():

    o = Example(dict(a=1, b="h", c=2.0, d=True))
    assert o.a == 1
    assert o.b == "h"
    assert o.c == 2.0
    assert o.d is True

    try:
        o = Example(dict(a=1, b=3, c=2.0, d=True))
        assert False
    except Exception as e:
        assert e == exceptions.WrongTypeError("b", 3, str)

    o = Example(dict(a=1, b=3, c=2.0, d=True), raise_on_error=False)
    errs = o.get_errors()
    assert isinstance(errs, tuple)
    assert len(errs) == 1
    e = errs[0]
    assert e == exceptions.WrongTypeError("b", 3, str)


def test_missing():

    o = Example(dict(a=1, c=2.0, d=True), err_on_missing=False)
    assert o.a == 1
    assert o.c == 2.0
    assert o.d is True

    try:
        o = Example(dict(a=1, c=2.0, d=False))
        assert False
    except Exception as e:
        assert e == exceptions.MissingValueError("b")

    o = Example(dict(a=1, c=2.0, d=True), raise_on_error=False)
    errs = o.get_errors()
    assert isinstance(errs, tuple)
    assert len(errs) == 1
    e = errs[0]
    assert e == exceptions.MissingValueError("b")


def test_unexpected():

    o = Example(dict(a=1, b="h", c=2.0, d=True, e=5), err_on_unexpected=False)
    assert o.a == 1
    assert o.b == "h"
    assert o.c == 2.0
    assert o.d is True

    try:
        o = Example(dict(a=1, b="h", c=2.0, d=True, e=5))
        assert False
    except Exception as e:
        assert e == exceptions.UnexpectedKeyError("e", 5)

    o = Example(dict(a=1, b="h", c=2.0, d=True, e=5), raise_on_error=False)
    errs = o.get_errors()
    assert isinstance(errs, tuple)
    assert len(errs) == 1
    e = errs[0]
    assert e == exceptions.UnexpectedKeyError("e", 5)


def test_example_default():

    o = ExampleWithDefault(dict(a=1))
    assert o.a == 1
    assert o.b == "h"


def test_nested():

    arg = dict(a=1, n=dict(a=2))
    o = ExampleNested(arg)
    assert o.a == 1
    assert o.n.a == 2

    arg = dict(a=1, n=dict(c=3))
    errs = (
        exceptions.UnexpectedKeyError("c", 3, parents=("n",)),
        exceptions.MissingValueError("a", parents=("n",)),
    )

    try:
        o = ExampleNested(arg)
        assert False
    except Exception as e:
        assert e == errs[0]

    o = ExampleNested(arg, raise_on_error=False)
    assert o.get_errors() == errs


def test_nested_list():

    arg = dict(a=1, n=[dict(a=2)])
    o = ExampleNestedList(arg)
    assert o.a == 1
    assert o.n[0].a == 2

    arg = dict(a=1, n=[dict(c=3)])
    try:
        o = ExampleNestedList(arg)
        assert False
    except Exception as e:
        assert e == exceptions.UnexpectedKeyError("c", 3, parents=("n[0]",))


def test_nested_tuple():

    arg = dict(a=1, n=(dict(a=2),))
    o = ExampleNestedTuple(arg)
    assert o.a == 1
    assert o.n[0].a == 2

    arg = dict(a=1, n=(dict(c=3),))
    try:
        o = ExampleNestedTuple(arg)
        assert False
    except Exception as e:
        assert e == exceptions.UnexpectedKeyError("c", 3, parents=("n[0]",))


def test_nested_dict():

    arg = dict(a=1, n=dict(k=dict(a=2)))
    o = ExampleNestedDict(arg)
    assert o.a == 1
    assert o.n["k"].a == 2

    arg = dict(a=1, n=dict(k=dict(c=3)))
    try:
        o = ExampleNestedDict(arg)
        assert False
    except Exception as e:
        assert e == exceptions.UnexpectedKeyError("c", 3, parents=("n['k']",))
