"""
    datastruct.typing_ext
    ~~~~~~~~~~~~~~~~~~~~~

    Extension for the python typing module.

    Adapted from https://stackoverflow.com/questions/49171189/whats-the-correct-way-to-check-if-an-object-is-a-typing-generic

    :copyright: 2020 by datastruct Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

# DataStruct only supports Python 3.7+
# Therefore, we remove from the coverage report the corresponding sections.
# But we keep the code because it is convenient
# to have just one file like this across projects.

import typing

if hasattr(typing, "_GenericAlias"):
    # python 3.7 and 3.8
    def _is_generic(cls):
        if isinstance(cls, typing._GenericAlias):
            return True

        if isinstance(cls, typing._SpecialForm):
            return cls not in {typing.Any}

        return False

    try:
        # Python 3.8
        Prot = typing.Protocol
        VGA = typing._VariadicGenericAlias
    except AttributeError:
        # Python 3.7
        Prot = typing._Protocol
        VGA = typing._VariadicGenericAlias

    def _is_base_generic(cls):
        if isinstance(cls, typing._GenericAlias):
            if cls.__origin__ in {typing.Generic, Prot}:
                return False

            if isinstance(cls, VGA):
                return True

            return len(cls.__parameters__) > 0

        if isinstance(cls, typing._SpecialForm):
            return cls._name in {"ClassVar", "Union", "Optional"}

        return False


else:  # pragma: no cover
    # python <3.7
    if hasattr(typing, "_Union"):
        # python 3.6
        def _is_generic(cls):
            if isinstance(
                cls,
                (typing.GenericMeta, typing._Union, typing._Optional, typing._ClassVar),
            ):
                return True

            return False

        def _is_base_generic(cls):
            if isinstance(cls, (typing.GenericMeta, typing._Union)):
                return cls.__args__ in {None, ()}

            if isinstance(cls, typing._Optional):
                return True

            return False

    else:
        # python 3.5
        def _is_generic(cls):
            if isinstance(
                cls,
                (
                    typing.GenericMeta,
                    typing.UnionMeta,
                    typing.OptionalMeta,
                    typing.CallableMeta,
                    typing.TupleMeta,
                ),
            ):
                return True

            return False

        def _is_base_generic(cls):
            if isinstance(cls, typing.GenericMeta):
                return all(
                    isinstance(arg, typing.TypeVar) for arg in cls.__parameters__
                )

            if isinstance(cls, typing.UnionMeta):
                return cls.__union_params__ is None

            if isinstance(cls, typing.TupleMeta):
                return cls.__tuple_params__ is None

            if isinstance(cls, typing.CallableMeta):
                return cls.__args__ is None

            if isinstance(cls, typing.OptionalMeta):
                return True

            return False


def is_generic(cls):
    """
    Detects any kind of generic, for example `List` or `List[int]`. This includes "special" types like
    Union and Tuple - anything that's subscriptable, basically.
    """
    return _is_generic(cls)


def is_base_generic(cls):
    """
    Detects generic base classes, for example `List` (but not `List[int]`)
    """
    return _is_base_generic(cls)


def is_qualified_generic(cls):
    """
    Detects generics with arguments, for example `List[int]` (but not `List`)
    """
    return is_generic(cls) and not is_base_generic(cls)
