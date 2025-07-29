"""Helper util functions for the models module."""

import json
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

_MAX_DOMAIN_ID_LENGTH = 64

MAX_MPTOKEN_METADATA_LENGTH = 1024 * 2

MAX_MPT_META_TOP_LEVEL_FIELD_COUNT = 9

MPT_META_URL_FIELD_COUNT = 3

TICKER_REGEX = re.compile(r"^[A-Z0-9]{1,6}$")

MPT_META_REQUIRED_FIELDS = [
    "ticker",
    "name",
    "icon",
    "asset_class",
    "issuer_name",
]

MPT_META_ASSET_CLASSES = [
    "rwa",
    "memes",
    "wrapped",
    "gaming",
    "defi",
    "other",
]

MPT_META_ASSET_SUB_CLASSES = [
    "stablecoin",
    "commodity",
    "real_estate",
    "private_credit",
    "equity",
    "treasury",
    "other",
]

MPT_META_WARNING_HEADER = (
    "MPTokenMetadata is not properly formatted as JSON as per the XLS-89d standard. "
    "While adherence to this standard is not mandatory, such non-compliant MPToken's "
    "might not be discoverable by Explorers and Indexers in the XRPL ecosystem."
)


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


def validate_domain_id(domain_id: str) -> str:
    """
    Validates the DomainID string for correct hexadecimal format and length.

    Args:
        domain_id: The DomainID to validate. Expected to be a 64-character hexadecimal
            string representing a Hash256 value on XRPL.

    Returns:
        An error message if the domain_id is invalid; otherwise, an empty string.
        Possible error cases include incorrect length or presence of non-hexadecimal
        characters.
    """
    if not isinstance(domain_id, str) or len(domain_id) != _MAX_DOMAIN_ID_LENGTH:
        return "domain_id length must be 64 characters."
    if not HEX_REGEX.fullmatch(domain_id):
        return "domain_id must only contain hexadecimal characters."
    return ""


def _is_valid_mpt_url_structure(input_data: Any) -> bool:  # noqa: ANN401
    return (
        isinstance(input_data, Dict)
        and isinstance(input_data.get("url"), str)
        and isinstance(input_data.get("type"), str)
        and isinstance(input_data.get("title"), str)
        and len(input_data.keys()) == MPT_META_URL_FIELD_COUNT
    )


def validate_mptoken_metadata(input_hex: str) -> List[str]:
    """
    Validates if MPTokenMetadata adheres to XLS-89d standard.

    Args:
        input_hex (str): Hex encoded MPTokenMetadata.

    Returns:
        List[str]: A list of validation error messages.
    """
    from xrpl.utils.str_conversions import hex_to_str

    validation_messages: List[str] = []

    if bool(HEX_REGEX.fullmatch(input_hex)) is False:
        validation_messages.append("MPTokenMetadata must be in hex format.")
        return validation_messages

    if len(input_hex) == 0 or len(input_hex) > MAX_MPTOKEN_METADATA_LENGTH:
        validation_messages.append(
            (
                "MPTokenMetadata must be non-empty and max "
                f"{int(MAX_MPTOKEN_METADATA_LENGTH / 2)} bytes."
            )
        )
        return validation_messages

    try:
        decoded_str = hex_to_str(input_hex)
        json_metadata = json.loads(decoded_str)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        validation_messages.append(
            f"MPTokenMetadata is not properly formatted as JSON - {str(e)}"
        )
        return validation_messages

    if not isinstance(json_metadata, Dict):
        validation_messages.append(
            "MPTokenMetadata is not properly formatted as per XLS-89d."
        )
        return validation_messages

    # Structure validation

    field_count = len(json_metadata.keys())
    if field_count > MAX_MPT_META_TOP_LEVEL_FIELD_COUNT:
        validation_messages.append(
            (
                "MPTokenMetadata must not contain more than "
                f"{MAX_MPT_META_TOP_LEVEL_FIELD_COUNT} top-level fields "
                f"(found {field_count})."
            )
        )
        return validation_messages

    for field in MPT_META_REQUIRED_FIELDS:
        if not isinstance(json_metadata.get(field), str):
            validation_messages.append(f"{field} is required and must be string.")

    if len(validation_messages) > 0:
        return validation_messages

    if "desc" in json_metadata and not isinstance(json_metadata["desc"], str):
        validation_messages.append("desc must be a string.")
        return validation_messages

    if "asset_subclass" in json_metadata and not isinstance(
        json_metadata["asset_subclass"], str
    ):
        validation_messages.append("asset_subclass must be a string.")
        return validation_messages

    additional_info = json_metadata.get("additional_info")
    if additional_info is not None and not isinstance(additional_info, (str, dict)):
        validation_messages.append("additional_info must be a string or JSON object.")
        return validation_messages

    if "urls" in json_metadata:
        urls = json_metadata["urls"]
        if not isinstance(urls, list):
            validation_messages.append("urls must be an array as per XLS-89d.")
            return validation_messages

        if not all(_is_valid_mpt_url_structure(u) for u in urls):
            validation_messages.append(
                "One or more urls are not structured per XLS-89d."
            )
            return validation_messages

    # Content validation
    ticker = json_metadata["ticker"]
    if not TICKER_REGEX.match(ticker):
        validation_messages.append(
            (
                "ticker should have uppercase letters (A-Z) and digits (0-9) only. "
                "Max 6 characters recommended."
            )
        )

    if not json_metadata["icon"].startswith("https://"):
        validation_messages.append("icon should be a valid https url.")

    asset_class = json_metadata["asset_class"].lower()
    if asset_class not in MPT_META_ASSET_CLASSES:
        validation_messages.append(
            f"asset_class should be one of {', '.join(MPT_META_ASSET_CLASSES)}."
        )

    asset_subclass = json_metadata.get("asset_subclass")
    if (
        asset_subclass is not None
        and asset_subclass.lower() not in MPT_META_ASSET_SUB_CLASSES
    ):
        validation_messages.append(
            "asset_subclass should be one of "
            f"{', '.join(MPT_META_ASSET_SUB_CLASSES)}."
        )

    if asset_class == "rwa" and asset_subclass is None:
        validation_messages.append(
            "asset_subclass is required when asset_class is rwa."
        )

    if "urls" in json_metadata:
        urls = json_metadata["urls"]
        for url in urls:
            if not url["url"].startswith("https://"):
                validation_messages.append("url should be a valid https url.")
                break

    return validation_messages


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
