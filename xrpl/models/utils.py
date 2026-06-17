"""Helper util functions for the models module."""

import re
from typing import Dict, List, Optional, Pattern

from typing_extensions import Final

HEX_REGEX: Final[Pattern[str]] = re.compile("[a-fA-F0-9]*")

MAX_CREDENTIAL_ARRAY_LENGTH = 8

# Credentials are represented in hex. Whilst they are allowed a maximum length of 64
# bytes, every byte requires 2 hex characters for representation
_MAX_CREDENTIAL_LENGTH: Final[int] = 128

_MAX_DOMAIN_ID_LENGTH = 64

MAX_MPTOKEN_METADATA_LENGTH = 1024 * 2

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
