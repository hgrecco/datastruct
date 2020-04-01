"""
    datastruct.ds
    ~~~~~~~~~~~~~

    Definition of the DataStruct class.

    :copyright: 2020 by datastruct Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

import inspect
import typing
from typing import List, Tuple, get_type_hints

import serialize

from . import exceptions, typing_ext


def _func_for_annotation(key, annotation, ds_kw):
    """This recapitulates the same logic as the DS.__init__ for a single element.

    TODO: check if it we can avoid this repetirion

    Parameters
    ----------
    key : str
    annotation

    Returns
    -------

    """

    if inspect.isclass(annotation) and issubclass(annotation, DataStruct):

        def func(el):
            try:
                cel = annotation(el, **ds_kw)
            except exceptions.ValidationError as exc:
                return exc
            return cel

    elif inspect.isclass(annotation) and issubclass(annotation, KeyDefinedValue):

        def func(el):
            try:
                cel = annotation.convert(key, el, **ds_kw)
            except exceptions.ValidationError as exc:
                raise exc

            return cel

    elif hasattr(annotation, "validate"):

        def func(el):

            if not annotation.validate(el):
                return exceptions.WrongValueError(key, el, annotation)

            return el

    else:

        def func(el):
            if not isinstance(el, annotation):
                return exceptions.WrongTypeError(key, el, annotation)
            return el

    return func


def _apply_func(ds, func, parent_key, value):
    cel = func(value)

    if isinstance(cel, exceptions.ValidationError):
        ds._found_error(cel.with_parent(parent_key))

    elif isinstance(cel, DataStruct):
        for err in cel.get_errors():
            ds._found_error(err.with_parent(parent_key))

    return cel


def with_qualified_container(ds: "DataStruct", key, value, annotation, ds_kw):

    container = annotation.__origin__

    if container is typing.Union:

        ds_kw_copy = dict(ds_kw)
        ds_kw_copy["raise_on_error"] = True

        for t in annotation.__args__:

            func = _func_for_annotation(key, t, ds_kw_copy)
            try:
                return _apply_func(ds, func, key, value)
            except exceptions.ValidationError:
                # If there was an error, try the next.
                continue

        ds._found_error(exceptions.WrongValueError(key, value, annotation))

    elif container is dict:
        funck = _func_for_annotation(key, annotation.__args__[0], ds_kw)
        funcv = _func_for_annotation(key, annotation.__args__[1], ds_kw)

        tmp = []
        for ndx, (elk, elv) in enumerate(value.items()):

            celk = _apply_func(ds, funck, "%s[%r]" % (key, elk), elk)
            celv = _apply_func(ds, funcv, "%s[%r]" % (key, elk), elv)

            tmp.append((celk, celv))

        return container(tmp)

    elif container in (list, tuple):
        func = _func_for_annotation(key, annotation.__args__[0], ds_kw)

        tmp = []
        for ndx, el in enumerate(value):

            cel = _apply_func(ds, func, "%s[%d]" % (key, ndx), el)

            tmp.append(cel)

        return container(tmp)

    else:
        raise Exception(container)


class DataStruct:
    """Base classes for data structures.

    Parameters
    ----------
    content : dict
    raise_on_error : bool
        If true, an exception will be raised. If false, the exception will be recorded.
    err_on_unexpected : bool
        If true, an unexpected value
    err_on_missing : bool
    """

    def __init__(
        self,
        content,
        *,
        raise_on_error=True,
        err_on_unexpected=True,
        err_on_missing=True,
    ):

        self.__raise_on_error__ = raise_on_error

        #: Errors found when filling the data structure.
        self.__errors__: List[exceptions.ValidationError] = []

        th = get_type_hints(self.__class__)

        samekw = dict(
            raise_on_error=raise_on_error,
            err_on_unexpected=err_on_unexpected,
            err_on_missing=err_on_missing,
        )

        # Rationale: Part 1
        #   We iterate over the items provided to fill the DataStructure
        #   and try to assign them to the corresponding attribute.
        #
        #   If a value is invalid, it is not used.

        for key, value in content.items():

            # (1) If the attribute is not specified in the schema,
            #     we report it and move on.
            try:
                k_annot = th.pop(key)
            except KeyError:
                self._found_error(
                    exceptions.UnexpectedKeyError(
                        key, value, warning=not err_on_unexpected
                    )
                )
                continue

            # (2) If a DataStruct subclass is expected for this attribute,
            #     we instance an object, check for errors and move on.
            if inspect.isclass(k_annot) and issubclass(k_annot, DataStruct):
                try:
                    value = k_annot(value, **samekw)
                except exceptions.ValidationError as exc:
                    raise exc.with_parent(key)

                if value.__errors__:
                    for err in value.__errors__:
                        self._found_error(err.with_parent(key))
                else:
                    setattr(self, key, value)

            # ### C
            elif inspect.isclass(k_annot) and issubclass(k_annot, KeyDefinedValue):
                try:
                    value = k_annot.convert(key, value, **samekw)
                except exceptions.ValidationError as exc:
                    raise exc.with_parent(key)

                if value.__errors__:
                    for err in value.__errors__:
                        self._found_error(err.with_parent(key))
                else:
                    setattr(self, key, value)

            # (3) If the annotation type has a validate method,
            #     we call it with the value.
            #     If it fails, we report the the
            elif hasattr(k_annot, "validate"):
                if k_annot.validate(value):
                    setattr(self, key, value)
                else:
                    self._found_error(exceptions.WrongValueError(key, value, k_annot))

            # (4) If the annotation type is a Qualified Generic (e.g. List[int],
            #     we verify both the container and the content match between schema and value.
            elif typing_ext.is_qualified_generic(k_annot):

                container = k_annot.__origin__
                if container is typing.Union:
                    setattr(
                        self,
                        key,
                        with_qualified_container(self, key, value, k_annot, samekw),
                    )
                elif not isinstance(value, container):
                    self._found_error(exceptions.WrongTypeError(key, value, container))
                else:
                    setattr(
                        self,
                        key,
                        with_qualified_container(self, key, value, k_annot, samekw),
                    )

            # (4) Base Generic (e.g. List) are not supported, use list instead
            #
            # TODO: This should be catch on class creation.
            elif typing_ext.is_base_generic(k_annot):
                raise Exception(
                    "Invalid schema for %s.%s - Base Generics are not supported"
                    % (self.__class__.__name__, key)
                )

            # (5) If the annotation type is a a type,
            #     we verify
            elif isinstance(k_annot, type):
                if not isinstance(value, k_annot):
                    self._found_error(exceptions.WrongTypeError(key, value, k_annot))
                else:
                    setattr(self, key, value)

            # (6) Other cases are not supported.
            #
            # TODO: This should be catch on class creation.
            else:
                raise Exception(
                    "Invalid schema for %s.%s" % (self.__class__.__name__, key)
                )

        # Rationale: Part 2
        #   We then iterate over the annotations that have not been consumed by a provided items
        #   and report an error if there is no default value.
        for key, value in th.items():
            if not hasattr(self, key):
                self._found_error(
                    exceptions.MissingValueError(key, warning=not err_on_missing)
                )

    def _found_error(self, exc: exceptions.ValidationError):
        if self.__raise_on_error__ and not exc.warning:
            raise exc

        self.__errors__.append(exc)

    def get_errors(self) -> Tuple[exceptions.ValidationError]:
        """Get the list of errors found when parsing this structure.

        Only available when `raise_on_error` is False.

        Returns
        -------
        tuple of Exceptions

        """

        return tuple(self.__errors__)

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
        Returns
        -------
        BaseStruct
        """

        return cls(
            serialize.load(filename, fmt),
            raise_on_error=raise_on_error,
            err_on_unexpected=err_on_unexpected,
            err_on_missing=err_on_missing,
        )


class KeyDefinedValue:

    content: dict

    @classmethod
    def convert(
        cls,
        key,
        value,
        raise_on_error=True,
        err_on_unexpected=True,
        err_on_missing=True,
    ):
        if not isinstance(value, dict):
            raise exceptions.WrongTypeError(key, value, dict)

        if len(value) != 1:
            raise exceptions.WrongValueError(key, value, "Len 1")

        k, v = dict(value).popitem()

        if k not in cls.content:
            raise exceptions.WrongValueError(
                key, value, "value in %r" % tuple(cls.content.keys())
            )

        expected = cls.content[k]

        samekw = dict(
            raise_on_error=raise_on_error,
            err_on_unexpected=err_on_unexpected,
            err_on_missing=err_on_missing,
        )
        func = _func_for_annotation(key, expected, samekw)

        return func(v)
