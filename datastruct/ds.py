"""
    datastruct.ds
    ~~~~~~~~~~~~~

    Definition of the DataStruct class.

    :copyright: 2020 by datastruct Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

import inspect
import typing
from collections import ChainMap
from typing import Iterable, List, Tuple, get_type_hints

import serialize

from . import exceptions, typing_ext


class _INVALID:
    def __str__(self):
        return "<INVALID>"

    __repr__ = __str__


INVALID = _INVALID()


class ValueAndError:
    """This class provides a comm
    """

    def __init__(self, value, error=()):
        self.value = value
        self.error = error

    def get_errors(self) -> Tuple[exceptions.ValidationError]:
        out = []
        if isinstance(self.value, dict):
            for k, v in self.value.items():
                out.extend((exc.with_parent("in key") for exc in k.get_errors()))
                out.extend((exc.with_index(k.flatten()) for exc in v.get_errors()))

        elif isinstance(self.value, (list, tuple)):
            for ndx, el in enumerate(self.value):
                out.extend((exc.with_index(ndx) for exc in el.get_errors()))

        elif isinstance(self.value, self.__class__):
            out.extend(self.value.get_errors())

        elif isinstance(self.value, DataStruct):
            out.extend(self.value.get_errors())

        if isinstance(self.error, exceptions.ValidationError):
            out.append(self.error)

        return tuple(out)

    @classmethod
    def from_exc(cls, exc: exceptions.ValidationError):
        return cls(INVALID, exc)

    @classmethod
    def auto(cls, value):
        if isinstance(value, exceptions.ValidationError):
            return cls.from_exc(value)
        return cls(value)

    def flatten(self):
        if isinstance(self.value, dict):
            return {k.flatten(): v.flatten() for k, v in self.value.items()}
        elif isinstance(self.value, list):
            return [el.flatten() for el in self.value]
        elif isinstance(self.value, tuple):
            return tuple(el.flatten() for el in self.value)
        elif isinstance(self.value, self.__class__):
            return self.value.flatten()
        elif isinstance(self.value, DataStruct):
            return self.value.flatten()
        else:
            return self.value


def convert(annotation, value):
    """This recapitulates the same logic as the DS.__init__ for a single element.

    Parameters
    ----------
    annotation

    Returns
    -------

    """

    # (1) The annotation is a DataStruct subclass.
    if inspect.isclass(annotation) and issubclass(annotation, DataStruct):

        return annotation(value)

    # (2) The annotation is a KeyDefinedValue subclass.
    elif inspect.isclass(annotation) and issubclass(annotation, KeyDefinedValue):

        if not isinstance(value, dict):
            return ValueAndError.from_exc(exceptions.WrongTypeError(value, dict))

        if len(value) != 1:
            return ValueAndError.from_exc(exceptions.WrongValueError(value, "Len 1"))

        k, v = dict(value).popitem()

        if k not in annotation.content:
            return ValueAndError.from_exc(
                exceptions.WrongValueError(
                    k, "key in %s" % repr(tuple(annotation.content.keys()))
                )
            )

        return convert(annotation.content[k], v)

    # (3) The annotation type has a validate method.
    elif hasattr(annotation, "validate"):

        if annotation.validate(value):
            return ValueAndError(value)
        else:
            return ValueAndError.from_exc(exceptions.WrongValueError(value, annotation))

    # (4) The annotation type is a Qualified Generic (e.g. List[int])
    elif typing_ext.is_qualified_generic(annotation):

        container_type = annotation.__origin__
        internal_annotations = annotation.__args__

        if container_type is typing.Union:
            for t in internal_annotations:
                out = convert(t, value)
                if not isinstance(out, exceptions.ValidationError):
                    return ValueAndError(out)
            else:
                return ValueAndError.from_exc(
                    exceptions.WrongValueError(value, "Union of {internal_types}")
                )

        if not isinstance(value, container_type):
            return ValueAndError.from_exc(
                exceptions.WrongTypeError(value, container_type)
            )

        if container_type is dict:

            tmp = []

            for ndx, (elk, elv) in enumerate(value.items()):
                celk = convert(internal_annotations[0], elk)
                celv = convert(internal_annotations[1], elv)

                tmp.append((ValueAndError.auto(celk), ValueAndError.auto(celv)))

            return ValueAndError(dict(tmp))

        elif container_type in (list, tuple):

            tmp = []
            for ndx, el in enumerate(value):
                cel = convert(internal_annotations[0], el)

                tmp.append(ValueAndError.auto(cel))

            return ValueAndError(container_type(tmp))

        else:
            raise TypeError(f"Unknown container type {container_type}")

    # (5) The annotation type is a Base Generic (e.g. List). Not supported, use list instead.
    elif typing_ext.is_base_generic(annotation):
        raise Exception(
            "This should have been catched as subclass creation. "
            "Please open an issue."
        )

    # (6) If the annotation type is a a type
    elif isinstance(annotation, type):

        if isinstance(value, annotation):
            return ValueAndError(value)
        else:
            return ValueAndError.from_exc(exceptions.WrongTypeError(value, annotation))

    # (7) Other cases are not supported.
    else:
        raise Exception(
            "This should have been catched as subclass creation. "
            "Please open an issue."
        )


class DataStruct:
    """Base classes for data structures.

    Parameters
    ----------
    content : Mapping

    """

    def __init_subclass__(cls, **kwargs):
        errs = []
        for name, annotation in cls.__annotations__.items():
            if inspect.isclass(annotation) and issubclass(annotation, DataStruct):
                continue
            elif inspect.isclass(annotation) and issubclass(
                annotation, KeyDefinedValue
            ):
                continue
            elif hasattr(annotation, "validate"):
                continue
            elif typing_ext.is_qualified_generic(annotation):
                continue
            elif typing_ext.is_base_generic(annotation):
                errs.append(
                    f"In {name}, {annotation} is an invalid annotation. "
                    f"Based generics (e.g. List) are allowed, used types (e.g. list) instead."
                )
            elif isinstance(annotation, type):
                continue
            else:
                errs.append(
                    f"In {name}, {annotation} is an unknown kind of annotation."
                )
        if errs:
            raise TypeError(
                f"Class {cls.__name__} failed to initialize the following attributes: {errs}"
            )
        super().__init_subclass__(**kwargs)

    def __init__(self, content):

        #: Errors found when filling the data structure.
        self.__errors__: List[exceptions.ValidationError] = []

        th = get_type_hints(self.__class__)

        #: Dict[str, Union[DataStruct, ValueAndError]]
        new_content = {}

        # Rationale: Part 1
        #   We iterate over the items provided to fill the DataStructure
        #   and try to assign them to the corresponding attribute.
        #
        #   If a value is invalid, it is not used.

        for key, value in content.items():

            # (1) If the attribute is not specified in the schema,
            #     we report it and move on.
            try:
                annotation = th.pop(key)
            except KeyError:
                self.__errors__.append(
                    exceptions.UnexpectedKeyError(key, self.__class__)
                )
                continue

            # (2) We build a dictionary with the content.
            new_content[key] = convert(annotation, value)

        # Rationale: Part 2
        #   We then iterate over the annotations that have not been consumed by a provided items
        #   and report an error if there is no default value.
        for key, value in th.items():
            if not hasattr(self, key):
                self.__errors__.append(
                    exceptions.MissingValueError(key, self.__class__)
                )

        for key, value in new_content.items():
            self.__errors__.extend((exc.with_parent(key) for exc in value.get_errors()))
            setattr(self, key, value.flatten())

    def flatten(self):
        return self

    def get_errors(
        self, err_on_unexpected=True, err_on_missing=True
    ) -> Tuple[exceptions.ValidationError]:
        """Get the list of errors found when parsing this structure.

        Only available when `raise_on_error` is False.

        Returns
        -------
        tuple of Exceptions

        """
        ignortypes = []
        if not err_on_missing:
            ignortypes.append(exceptions.MissingValueError)
        if not err_on_unexpected:
            ignortypes.append(exceptions.UnexpectedKeyError)

        if ignortypes:
            return tuple(
                exc for exc in self.__errors__ if not isinstance(exc, ignortypes)
            )
        else:
            return tuple(self.__errors__)

    @classmethod
    def from_dict(
        cls, dct, *, raise_on_error=True, err_on_unexpected=True, err_on_missing=True
    ):
        """Load the content of a dictionary into this datastructure

        Works just like instantiating the object but adds the ability to raise exceptions.

        Parameters
        ----------
        dct : mapping
        raise_on_error : bool
            If true, an exception will be raised. If false, the exception will be recorded.
        err_on_unexpected : bool
            If true, an unexpected value will produce an error.
            If false, only a warning is issued.
        err_on_missing : bool
            If true, a missing value will produce an error.
            If false, only a warning is issued.

        Returns
        -------
        DataStruct
        """

        ds = cls(dct)

        if raise_on_error:
            errs = ds.get_errors(err_on_unexpected, err_on_missing)
            if len(errs) == 1:
                raise errs[0]
            elif len(errs) > 1:
                raise exceptions.MultipleError(*errs)

        return ds

    @classmethod
    def from_filename(
        cls,
        filename: str,
        fmt=None,
        *,
        raise_on_error=True,
        err_on_unexpected=True,
        err_on_missing=True,
    ):
        """Load the content of a filename into this datastructure

        This leverages the serialize library.

        Parameters
        ----------
        filename : str
        fmt : str or None
            File format. Use None (default) to infer from the extension)
        raise_on_error : bool
            If true, an exception will be raised. If false, the exception will be recorded.
        err_on_unexpected : bool
            If true, an unexpected value will produce an error.
            If false, only a warning is issued.
        err_on_missing : bool
            If true, a missing value will produce an error.
            If false, only a warning is issued.

        Returns
        -------
        DataStruct
        """

        return cls.from_dict(
            serialize.load(filename, fmt),
            raise_on_error=raise_on_error,
            err_on_unexpected=err_on_unexpected,
            err_on_missing=err_on_missing,
        )

    @classmethod
    def from_filenames(
        cls,
        filenames: Iterable[str],
        fmt=None,
        *,
        raise_on_error=True,
        err_on_unexpected=True,
        err_on_missing=True,
    ):
        """Load the content of a multiple filenames into this datastructure

        This leverages the serialize library.

        Parameters
        ----------
        filenames : List[str]
            Multiple filenames. The first has precedence over the last.
        raise_on_error : bool
            If true, an exception will be raised. If false, the exception will be recorded.
        err_on_unexpected : bool
            If true, an unexpected value will produce an error.
            If false, only a warning is issued.
        err_on_missing : bool
            If true, a missing value will produce an error.
            If false, only a warning is issued.

        Returns
        -------
        DataStruct
        """

        dct = ChainMap(*tuple(serialize.load(filename, fmt) for filename in filenames))
        return cls.from_dict(
            dct,
            raise_on_error=raise_on_error,
            err_on_unexpected=err_on_unexpected,
            err_on_missing=err_on_missing,
        )


class KeyDefinedValue:
    """KeyDefinedValues are those in which the type of the value is defined by the value
    of a string key.
    """

    content: dict
