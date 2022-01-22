"""
    datastruct
    ~~~~~~~~~~~~~

    A small but useful package to load, validate and use typed data structures, including configuration files.

    :copyright: 2020 by datastruct Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

from . import validators
from .ds import INVALID, DataStruct, KeyDefinedValue
from .exceptions import (
    MissingValueError,
    UnexpectedKeyError,
    ValidationError,
    WrongTypeError,
    WrongValueError,
)

try:
    from importlib.metadata import version
except ImportError:
    # Backport for Python < 3.8
    from importlib_metadata import version

try:  # pragma: no cover
    __version__ = version("datastruct")
except Exception:  # pragma: no cover
    # we seem to have a local copy not installed without setuptools
    # so the reported version will be unknown
    __version__ = "unknown"


__all__ = [
    __version__,
    validators,
    DataStruct,
    MissingValueError,
    UnexpectedKeyError,
    WrongTypeError,
    WrongValueError,
    ValidationError,
    KeyDefinedValue,
    INVALID,
]
