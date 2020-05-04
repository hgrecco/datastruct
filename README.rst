.. image:: https://img.shields.io/pypi/v/datastruct.svg
    :target: https://pypi.python.org/pypi/datastruct
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/l/datastruct.svg
    :target: https://pypi.python.org/pypi/datastruct
    :alt: License

.. image:: https://img.shields.io/pypi/pyversions/datastruct.svg
    :target: https://pypi.python.org/pypi/datastruct
    :alt: Python Versions

.. image:: https://travis-ci.org/hgrecco/datastruct.svg?branch=master
    :target: https://travis-ci.org/hgrecco/datastruct
    :alt: CI

.. image:: https://coveralls.io/repos/github/hgrecco/datastruct/badge.svg?branch=master
    :target: https://coveralls.io/github/hgrecco/datastruct?branch=master
    :alt: Coverage



datastruct
==========

A small but useful package to load, validate and use typed data structures, including configuration files.

You get:

- An easy way to define a typed hierarchical data structure.
- Hassle free definition nested structures.
- Loading from a variety of formats (json, yaml and everything supported by Serialize_),
- Error checking including: missing values, unexpected value, wrong type, wrong value.
- Easy to integrate in another app error reporting.


Installation
------------

.. code-block::

    pip install datastruct

Usage
-----

.. code-block:: python

    >>> from typing import List
    >>> from datastruct import DataStruct
    >>> class EmailServer(DataStruct):
    ...
    ...     host: str
    ...     port: int
    ...     username: str
    ...     password: str
    >>>
    >>> class Config(DataStruct):
    ...
    ...     download_path: str
    ...     email_servers: List[EmailServer]
    ...     wait_time: float
    >>>
    >>> cfg = Config.from_filename('settings.yaml')

When an invalid value is found, an exception will be raised.

If you want to accumulate all errors for inspection:

.. code-block:: python

    >>> cfg = Config.from_filename('settings.yaml', raise_on_error=False)
    >>> print(cfg.get_errors())

You can then use the `DataStruct` object in your code:

.. code-block:: python

    >>> print(cfg.email_servers[0].host)


See AUTHORS_ for a list of the maintainers.

To review an ordered list of notable changes for each version of a project,
see CHANGES_


.. _`Serialize`: https://github.com/hgrecco/serialize
.. _`AUTHORS`: https://github.com/hgrecco/datastruct/blob/master/AUTHORS
.. _`CHANGES`: https://github.com/hgrecco/datastruct/blob/master/CHANGES