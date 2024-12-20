"""Helper util functions for the models module."""

import re
from dataclasses import dataclass, is_dataclass
from typing import Any, Dict, List, Optional, Pattern, Type, TypeVar, cast

from typing_extensions import Final

from xrpl.models.exceptions import XRPLModelException

HEX_REGEX: Final[Pattern[str]] = re.compile("[a-fA-F0-9]*")

MAX_CREDENTIAL_ARRAY_LENGTH = 8

# Credentials are represented in hex. Whilst they are allowed a maximum length of 64
# bytes, every byte requires 2 hex characters for representation
_MAX_CREDENTIAL_LENGTH: Final[int] = 128


def get_credential_type_error(credential_type: str) -> Optional[str]:
    """
    Utility function for validating the CredentialType field in all
    transactions related to Credential.

    Args:
        credential_type: A hex-encoded value to identify the type of credential from
            the issuer.

    Returns:
        Errors, if any, during validation of credential_type field
    """
    errors = []
    # credential_type is a required field in this transaction
    if len(credential_type) == 0:
        errors.append("cannot be an empty string.")
    elif len(credential_type) > _MAX_CREDENTIAL_LENGTH:
        errors.append(f"Length cannot exceed {_MAX_CREDENTIAL_LENGTH}.")
    if not HEX_REGEX.fullmatch(credential_type):
        errors.append("credential_type field must be encoded in hex.")
    return " ".join(errors) if len(errors) > 0 else None


def validate_credential_ids(credential_list: Optional[List[str]]) -> Dict[str, str]:
    """
    Args:
        credential_list: An optional list of input credentials

    Returns:
        Errors pertaining to credential_ids field
    """
    errors: Dict[str, str] = {}
    if credential_list is None:
        return errors

    if len(credential_list) == 0:
        errors["credential_ids"] = "CredentialIDs list cannot be empty."
    elif len(credential_list) > MAX_CREDENTIAL_ARRAY_LENGTH:
        errors["credential_ids"] = (
            f"CredentialIDs list cannot exceed {MAX_CREDENTIAL_ARRAY_LENGTH}"
            + " elements."
        )

    if len(credential_list) != len(set(credential_list)):
        errors["credential_ids_duplicates"] = (
            "CredentialIDs list cannot contain duplicate values."
        )

    return errors


# Code source for requiring kwargs:
# https://gist.github.com/mikeholler/4be180627d3f8fceb55704b729464adb

_T = TypeVar("_T")
_Self = TypeVar("_Self")


def _is_kw_only_attr_defined_in_dataclass() -> bool:
    """
    Returns:
        Utility function to determine if the Python interpreter's version is older
        than 3.10. This information is used to check the presence of KW_ONLY attribute
        in the dataclass

    For ease of understanding, the output of this function should be equivalent to the
    below code, unless the `kw_only` attribute is backported to older versions of
    Python interpreter

    Returns:
    if sys.version_info.major < 3:
        return True
    return sys.version_info.minor < 10
    """
    return "kw_only" in dataclass.__kwdefaults__


# Python 3.10 and higer versions of Python enable a new KW_ONLY parameter in dataclass
# This dictionary is used to ensure that Ledger Objects constructors reject
# positional arguments. It obviates the need to maintain decorators for the same
# functionality and enbles IDEs to auto-complete the constructor arguments.
# KW_ONLY Docs: https://docs.python.org/3/library/dataclasses.html#dataclasses.KW_ONLY

# Unit tests that validate this behavior can be found at test_channel_authorize.py
# and test_sign.py files.
KW_ONLY_DATACLASS = (
    dict(kw_only=True) if _is_kw_only_attr_defined_in_dataclass() else {}
)


def require_kwargs_on_init(cls: Type[_T]) -> Type[_T]:
    """
    Force a dataclass's init function to only work if called with keyword arguments.
    If parameters are not positional-only, a TypeError is thrown with a helpful message.
    This function may only be used on dataclasses.

    This works by wrapping the __init__ function and dynamically replacing it.
    Therefore, stacktraces for calls to the new __init__ might look a bit strange. Fear
    not though, all is well.

    Note: although this may be used as a decorator, this is not advised as IDEs will no
    longer suggest parameters in the constructor. Instead, this is the recommended
    usage:
        from dataclasses import dataclass
        @dataclass
        class Foo:
            bar: str
        require_kwargs_on_init(Foo)

    Args:
        cls: The class that requires keyword arguments (must be a dataclass).

    Returns:
        The provided class, adding an error on init if positional args are provided.

    Raises:
        TypeError: If cls is None or is not a dataclass.
    """
    # error messages for dev help
    if cls is None:
        raise TypeError("Cannot call with cls=None")
    if not is_dataclass(cls):
        raise TypeError(
            f"This decorator only works on dataclasses. {cls.__name__} is not a "
            "dataclass."
        )

    original_init = cls.__init__

    def new_init(self: _Self, *args: List[Any], **kwargs: Dict[str, Any]) -> None:
        if len(args) > 0:
            raise XRPLModelException(
                f"{type(self).__name__}.__init__ only allows keyword arguments. "
                f"Found the following positional arguments: {args}"
            )
        original_init(self, **kwargs)

    # For Python v3.10 and above, the KW_ONLY attribute in data_class
    # performs the functionality of require_kwargs_on_init class.
    # When support for older versions of Python (earlier than v3.10) is removed, the
    # usage of require_kwargs_on_init decorator on model classes can also be removed.
    if not _is_kw_only_attr_defined_in_dataclass():
        cls.__init__ = new_init  # type: ignore
    return cast(Type[_T], cls)
