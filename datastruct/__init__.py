"""
    datastruct
    ~~~~~~~~~~~~~

    A small but useful package to load and validate typed data structures, including configuration files.

    :copyright: 2020 by datastruct Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

from . import validators
from .ds import DataStruct
from .exceptions import (
    MissingValueError,
    UnexpectedKeyError,
    ValidationError,
    WrongTypeError,
    WrongValueError,
)

__all__ = [
    validators,
    DataStruct,
    MissingValueError,
    UnexpectedKeyError,
    WrongTypeError,
    WrongValueError,
    ValidationError,
]
