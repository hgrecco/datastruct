import typing

from datastruct import DataStruct, KeyDefinedValue, exceptions, validators


class Example(DataStruct):
    a: int
    b: str
    c: float
    d: bool


class ExampleWithDefault(DataStruct):
    a: int
    b: str = "h"


def test_exceptions():
    assert exceptions.ValidationError(path="a") == exceptions.ValidationError(
        path=("a",)
    )
    errs = (
        exceptions.ValidationError(path=("a",)),
        exceptions.ValidationError(path=("b",)),
    )
    me = exceptions.MultipleError(*errs)
    assert exceptions.ValidationError(path=("a",)) in me
    assert exceptions.ValidationError(path=("k",)) not in me


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
    assert e == exceptions.MissingValueError("b", Example)


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


def test_validators():
    assert validators.Email.validate("test@gmail.com")
    assert not validators.Email.validate("test@gmail")
    assert not validators.Email.validate(123)

    assert validators.value_in(1, 2, 3).validate(1)
    assert not validators.value_in(1, 2, 3).validate(4)


def test_init_subclass():
    class KDV(KeyDefinedValue):
        content = {"a": 1}

    class SC(DataStruct):
        c1: Example
        c2: KDV
        c3: validators.Email
        c4: typing.List[int]
        # c5: typing.List
        c6: int

    assert SC

    try:

        class SC2(DataStruct):
            c1: Example
            c2: KDV
            c3: validators.Email
            c4: typing.List[int]
            c5: typing.List
            c6: int

        assert False

    except TypeError:
        assert True
