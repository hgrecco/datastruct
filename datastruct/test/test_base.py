from datastruct import DataStruct, exceptions


class Example(DataStruct):
    a: int
    b: str
    c: float
    d: bool


class ExampleWithDefault(DataStruct):
    a: int
    b: str = "h"


def test_simple():

    o = Example(dict(a=1, b="h", c=2.0, d=True))
    assert o.a == 1
    assert o.b == "h"
    assert o.c == 2.0
    assert o.d is True

    try:
        o = Example.from_dict(dict(a=1, b=3, c=2.0, d=True))
        assert False
    except Exception as e:
        assert e == exceptions.WrongTypeError(3, str).with_parent("b")

    o = Example(dict(a=1, b=3, c=2.0, d=True))
    errs = o.get_errors()
    assert isinstance(errs, tuple)
    assert len(errs) == 1
    e = errs[0]
    assert e == exceptions.WrongTypeError(3, str).with_parent("b")


def test_missing():

    o = Example(dict(a=1, c=2.0, d=True))
    assert o.a == 1
    assert o.c == 2.0
    assert o.d is True

    o = Example(dict(a=1, c=2.0, d=True))
    errs = o.get_errors()
    assert isinstance(errs, tuple)
    assert len(errs) == 1
    e = errs[0]
    assert e == exceptions.MissingValueError("b")


def test_unexpected():

    o = Example(dict(a=1, b="h", c=2.0, d=True, e=5))
    assert o.a == 1
    assert o.b == "h"
    assert o.c == 2.0
    assert o.d is True

    o = Example(dict(a=1, b="h", c=2.0, d=True, e=5))
    errs = o.get_errors()
    assert isinstance(errs, tuple)
    assert len(errs) == 1
    e = errs[0]
    assert e == exceptions.UnexpectedKeyError("e", Example)


def test_example_default():

    o = ExampleWithDefault(dict(a=1))
    assert o.a == 1
    assert o.b == "h"
