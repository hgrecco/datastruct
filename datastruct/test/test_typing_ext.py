import typing

from datastruct.typing_ext import is_base_generic, is_generic, is_qualified_generic


def test_generic():
    assert is_generic(typing.List)
    assert is_generic(typing.List[int])
    assert is_generic(typing.Dict)
    assert is_generic(typing.Dict[int, str])
    assert is_generic(typing.Union)
    assert is_generic(typing.Union[int, float])


def test_base_generic():
    assert is_base_generic(typing.List)
    assert not is_base_generic(typing.List[int])
    assert is_base_generic(typing.Dict)
    assert not is_base_generic(typing.Dict[int, str])
    assert is_base_generic(typing.Union)
    assert not is_base_generic(typing.Union[int, float])


def test_qualified_generic():
    assert not is_qualified_generic(typing.List)
    assert is_qualified_generic(typing.List[int])
    assert not is_qualified_generic(typing.Dict)
    assert is_qualified_generic(typing.Dict[int, str])
    assert not is_qualified_generic(typing.Union)
    assert is_qualified_generic(typing.Union[int, float])
