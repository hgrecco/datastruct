"""
    datastruct
    ~~~~~~~~~~~~~

    A small but useful package to load, validate and use typed data structures, including configuration files.

    :copyright: 2020 by datastruct Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

from functools import partial, reduce


def merge_two(a, b, path=None, raise_on_conflict=False):
    """Merge two dictionaries into a new one creating recursing all keys.

    Parameters
    ----------
    a : dict
    b : dict
    path : list
        use for debug purposes
    raise_on_conflict : bool
        if False, the first dict will have precedence

    Returns
    -------
    dict
    """
    if path is None:
        path = []

    out = {}
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                out[key] = merge_two(a[key], b[key], path=path + [str(key)])
            elif a[key] == b[key]:
                pass  # same leaf value
            else:
                if raise_on_conflict:
                    raise Exception("Conflict at %s" % ".".join(path + [str(key)]))
                else:
                    out[key] = a[key]
        else:
            out[key] = b[key]

    for key in a:
        if key not in b:
            out[key] = a[key]

    return out


def merge(dcts, raise_on_conflict=False):
    """Merge multiple dictionaries into a new one creating recursing all keys.

    Parameters
    ----------
    dcts : Iterable(dcts)
    raise_on_conflict : bool
        if False, the first dict will have precedence

    Returns
    -------
    dict
    """

    merger = partial(merge_two, raise_on_conflict=raise_on_conflict)

    return reduce(merger, dcts)
