from datastruct import DataStruct, exceptions


class ExampleSingle(DataStruct):
    a: int


class ExampleNested(DataStruct):

    b: int
    n1: ExampleSingle


class ExampleNestedNested(DataStruct):

    c: int
    n2: ExampleNested


def test_nested():

    arg = dict(b=1, n1=dict(a=2))
    o = ExampleNested(arg)
    assert o.b == 1
    assert o.n1.a == 2

    arg = dict(b=1, n1=dict(z=3))
    errs = (
        exceptions.UnexpectedKeyError("z", ExampleSingle, path=("n1",)),
        exceptions.MissingValueError("a", ExampleSingle, path=("n1",)),
    )

    o = ExampleNested(arg)
    assert o.get_errors() == errs


def test_nested_nested():

    arg = dict(c=3, n2=dict(b=2, n1=dict(a=1)))
    o = ExampleNestedNested(arg)
    assert o.c == 3
    assert o.n2.b == 2
    assert o.n2.n1.a == 1

    arg = dict(c=3, n2=dict(b=2, n1=dict(z=3)))
    errs = (
        exceptions.UnexpectedKeyError("z", ExampleSingle, path=("n2", "n1",)),
        exceptions.MissingValueError("a", ExampleSingle, path=("n2", "n1",)),
    )

    o = ExampleNestedNested(arg)
    assert o.get_errors() == errs
