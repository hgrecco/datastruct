"""
    datastruct.validators
    ~~~~~~~~~~~~~~~~~~~~~

    Validators for common use cases.

    - Email
    - IPAddress
    - URL
    - Domain


    We strongly leverage the `validators` library.

    :copyright: 2020 by datastruct Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

import validators


class Validator:
    """Base class for validators.
    """

    @classmethod
    def validate(self, instance):
        return False


class StrValidator(Validator):
    """Base class for all string validators.
    """

    func = lambda s: False

    @classmethod
    def validate(cls, instance):
        return isinstance(instance, str) and cls.func(instance)


class Email(StrValidator):
    func = validators.email


class IPAddress(StrValidator):
    func = validators.ip_address


class URL(StrValidator):
    func = validators.url


class Domain(StrValidator):
    func = validators.domain


def value_in(*valid_values):

    valid_values = set(valid_values)

    class Klass(Validator):
        @classmethod
        def validate(self, instance):
            return instance in valid_values

    return Klass
