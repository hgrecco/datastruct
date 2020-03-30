"""
    datastruct.typing_ext
    ~~~~~~~~~~~~~~~~~~~~~

    Extension for the python typing module.

    - Email
    - IPAddress
    - URL
    - Domain

    :copyright: 2020 by datastruct Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

import typing


def is_generic(cls):
    """Detects any kind of generic, for example `List` or `List[int]`. This includes "special" types like
    Union and Tuple - anything that's subscriptable, basically.
    """

    if isinstance(cls, typing._GenericAlias):
        return True

    if isinstance(cls, typing._SpecialForm):
        return cls not in {typing.Any}

    return False


def is_base_generic(cls):
    """Detects generic base classes, for example `List` (but not `List[int]`)
    """

    if isinstance(cls, typing._GenericAlias):
        if cls.__origin__ in {typing.Generic, typing._Protocol}:
            return False

        if isinstance(cls, typing._VariadicGenericAlias):
            return True

        return len(cls.__parameters__) > 0

    if isinstance(cls, typing._SpecialForm):
        return cls._name in {"ClassVar", "Union", "Optional"}

    return False


def is_qualified_generic(cls):
    """Detects generics with arguments, for example `List[int]` (but not `List`)
    """
    return is_generic(cls) and not is_base_generic(cls)
