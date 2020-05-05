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

    #: top-to-bottom path to reach location at which the error has ocurred.
    path: Tuple[str]

    def __init__(self, *, path=()):
        if isinstance(path, str):
            self.path = (path,)
        else:
            self.path = tuple(path)

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.path == other.path
            and getattr(self, "value", None) == getattr(other, "value", None)
            and getattr(self, "expected", None) == getattr(other, "expected", None)
            and getattr(self, "klass", None) == getattr(other, "klass", None)
        )

    def __repr__(self):

        parts = (
            (f"key={self.key}" if hasattr(self, "key") else ""),
            (f"value={self.value}" if hasattr(self, "value") else ""),
            (f"expected={self.expected}" if hasattr(self, "expected") else ""),
            (f"klass={self.klass}" if hasattr(self, "klass") else ""),
            (f"path={self.path}" if self.path else ""),
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

        kw = dict(path=(parent,) + self.path)

        if hasattr(self, "value"):
            kw["value"] = self.value
        if hasattr(self, "expected"):
            kw["expected"] = self.expected
        if hasattr(self, "klass"):
            kw["klass"] = self.klass
        if hasattr(self, "key"):
            kw["key"] = self.key

        return self.__class__(**kw)

    def with_index(self, index):
        """Return a new object of the same class prepending a new parent from index

        Parameters
        ----------
        index

        Returns
        -------
        a new object of the same class
        """

        return self.with_parent("[%s]" % index)


class MissingValueError(ValidationError):
    """A value required by the schema was not provided.
    """

    def __init__(self, key, klass, **kwargs):
        super().__init__(**kwargs)
        self.key = key
        self.klass = klass


class UnexpectedKeyError(ValidationError):
    """A key not defined in the schema was provided.
    """

    def __init__(self, key, klass, **kwargs):
        super().__init__(**kwargs)
        self.key = key
        self.klass = klass


class WrongTypeError(ValidationError):
    """A provided value was not of the correct type.
    """

    def __init__(self, value, expected, **kwargs):
        super().__init__(**kwargs)
        self.value = value
        self.expected = expected


class WrongValueError(ValidationError):
    """A provided value has the right type but the value is not in range o accepted.
    """

    def __init__(self, value, expected, **kwargs):
        super().__init__(**kwargs)
        self.value = value
        self.expected = expected


class MultipleError(ValidationError):
    def __init__(self, *errs):
        self.exceptions = errs

    def __contains__(self, item):
        return item in self.exceptions
