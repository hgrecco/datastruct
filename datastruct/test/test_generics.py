from typing import Dict, List, Tuple

import pytest

from datastruct import DataStruct, exceptions


class ExampleSingle(DataStruct):
    a: int


class ExampleDictInt(DataStruct):

    a: int
    n: Dict[str, int]


class ExampleNestedList(DataStruct):

    a: int
    n: List[ExampleSingle]


class ExampleNestedTuple(DataStruct):

    a: int
    n: Tuple[ExampleSingle]


class ExampleNestedDict(DataStruct):

    a: int
    n: Dict[str, ExampleSingle]


@pytest.mark.parametrize("atype", (List, Tuple))
def test_sequence_int(atype):
    class ExampleSequenceInt(DataStruct):

        a: int
        n: atype[int]

    bt = atype.__origin__

    arg = dict(a=1, n=bt([1, 2, 3]))
    o = ExampleSequenceInt(arg)
    assert o.a == 1
    assert o.n[2] == 3
    assert not o.get_errors()

    arg = dict(a=1, n=bt([1, 2, "s"]))
    o = ExampleSequenceInt(arg)
    errs = (exceptions.WrongTypeError("s", int).with_index(2).with_parent("n"),)
    assert o.get_errors() == errs


def test_tuple_int():

    arg = dict(a=1, n=(dict(a=2),))
    o = ExampleNestedTuple.from_dict(arg)
    assert o.a == 1
    assert o.n[0].a == 2
    assert not o.get_errors()

    arg = dict(a=1, n=(dict(c=3),))
    o = ExampleNestedTuple(arg)
    errs = (
        exceptions.UnexpectedKeyError("c", ExampleSingle)
        .with_index(0)
        .with_parent("n"),
        exceptions.MissingValueError("a", ExampleSingle).with_index(0).with_parent("n"),
    )
    assert o.get_errors() == errs


def test_dict_int():

    arg = dict(a=1, n=dict(k=dict(a=2)))
    o = ExampleNestedDict(arg)
    assert o.a == 1
    assert o.n["k"].a == 2
    assert not o.get_errors()

    arg = dict(a=1, n=dict(k=dict(c=3)))
    o = ExampleNestedDict(arg)
    errs = (
        exceptions.UnexpectedKeyError("c", ExampleSingle)
        .with_index("k")
        .with_parent("n"),
        exceptions.MissingValueError("a", ExampleSingle)
        .with_index("k")
        .with_parent("n"),
    )
    assert o.get_errors() == errs


def test_nested_list():

    arg = dict(a=1, n=[dict(a=2)])
    o = ExampleNestedList.from_dict(arg)
    assert o.a == 1
    assert o.n[0].a == 2
    assert not o.get_errors()

    arg = dict(a=1, n=[dict(c=3)])
    o = ExampleNestedList(arg)
    errs = (
        exceptions.UnexpectedKeyError("c", ExampleSingle)
        .with_index(0)
        .with_parent("n"),
        exceptions.MissingValueError("a", ExampleSingle).with_index(0).with_parent("n"),
    )
    assert o.get_errors() == errs


def test_nested_tuple():

    arg = dict(a=1, n=(dict(a=2),))
    o = ExampleNestedTuple(arg)
    assert o.a == 1
    assert o.n[0].a == 2
    assert not o.get_errors()

    arg = dict(a=1, n=(dict(c=3),))
    o = ExampleNestedTuple(arg)
    errs = (
        exceptions.UnexpectedKeyError("c", ExampleSingle)
        .with_index(0)
        .with_parent("n"),
        exceptions.MissingValueError("a", ExampleSingle).with_index(0).with_parent("n"),
    )
    assert o.get_errors() == errs


def test_nested_dict():

    arg = dict(a=1, n=dict(k=dict(a=2)))
    o = ExampleNestedDict(arg)
    assert o.a == 1
    assert o.n["k"].a == 2
    assert not o.get_errors()

    arg = dict(a=1, n=dict(k=dict(c=3)))
    o = ExampleNestedDict(arg)
    errs = (
        exceptions.UnexpectedKeyError("c", ExampleSingle)
        .with_index("k")
        .with_parent("n"),
        exceptions.MissingValueError("a", ExampleSingle)
        .with_index("k")
        .with_parent("n"),
    )
    assert o.get_errors() == errs
