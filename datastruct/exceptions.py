"""
    datastruct.exceptions
    ~~~~~~~~~~~~~~~~~~~~~

    Exceptions raised by the package.

    - MissingValueError
    - UnexpectedKeyError
    - WrongTypeError
    - WrongValueError

    :copyright: 2020 by datastruct Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

from typing import Tuple


class ValidationError(Exception):
    """Base class for all exceptions of the package.
    """

    #: Key in which the
    key: str

    #: Parents
    parents: Tuple[str]

    #: True when the error exists but the validator is not strict.
    warning: bool

    def __init__(self, *, parents=(), warning=False):
        self.parents = parents
        self.warning = warning

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.key == other.key
            and self.warning == other.warning
            and self.parents == other.parents
            and getattr(self, "value", None) == getattr(other, "value", None)
            and getattr(self, "expected", None) == getattr(other, "expected", None)
        )

    def __repr__(self):

        parts = (
            f"key={self.key}",
            (f"value={self.value}" if hasattr(self, "value") else ""),
            (f"expected={self.expected}" if hasattr(self, "expected") else ""),
            (f"parents={self.parents}" if self.parents else ""),
            (f"warning={self.warning}" if self.warning else ""),
        )

        return (
            f"{self.__class__.__name__}("
            + ", ".join(part for part in parts if part)
            + ")"
        )

    __str__ = __repr__

    def with_parent(self, parent: str):
        """Return a new object of the same class prepending a new parent.

        Parameters
        ----------
        parent : str
            a new parent

        Returns
        -------
        a new object of the same class
        """
        kw = dict(key=self.key)
        if hasattr(self, "value"):
            kw["value"] = self.value
        if hasattr(self, "expected"):
            kw["expected"] = self.expected
        kw.update(parents=(parent,) + self.parents, warning=self.warning)
        return self.__class__(**kw)


class MissingValueError(ValidationError):
    """A value required by the schema was not provided.
    """

    def __init__(self, key, **kwargs):
        super().__init__(**kwargs)
        self.key = key


class UnexpectedKeyError(ValidationError):
    """A key not defined in the schema was provided.
    """

    def __init__(self, key, value, **kwargs):
        super().__init__(**kwargs)
        self.key = key
        self.value = value


class WrongTypeError(ValidationError):
    """A provided value was not of the correct type.
    """

    def __init__(self, key, value, expected, **kwargs):
        super().__init__(**kwargs)
        self.key = key
        self.value = value
        self.expected = expected


class WrongValueError(ValidationError):
    """A provided value has the right type but the value is not in range o accepted.
    """

    def __init__(self, key, value, expected, **kwargs):
        super().__init__(**kwargs)
        self.key = key
        self.value = value
        self.expected = expected
