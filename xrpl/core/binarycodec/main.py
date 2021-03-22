"""High-level binary codec methods."""

from typing import Any, Dict, Optional, cast

from xrpl.core.binarycodec.binary_wrappers.binary_parser import BinaryParser
from xrpl.core.binarycodec.types.account_id import AccountID
from xrpl.core.binarycodec.types.hash256 import Hash256
from xrpl.core.binarycodec.types.serialized_dict import SerializedDict
from xrpl.core.binarycodec.types.uint64 import UInt64


def _num_to_bytes(num: int) -> bytes:
    return (num).to_bytes(4, byteorder="big", signed=False)


_TRANSACTION_SIGNATURE_PREFIX = _num_to_bytes(0x53545800)
_PAYMENT_CHANNEL_CLAIM_PREFIX = _num_to_bytes(0x434C4D00)
_TRANSACTION_MULTISIG_PREFIX = _num_to_bytes(0x534D5400)


def encode(json: Dict[str, Any]) -> str:
    """
    Encode a transaction.

    Args:
        json: the JSON representation of a transaction.

    Returns:
        A hex-string of the encoded transaction.
    """
    return cast(str, _serialize_json(json))


def encode_for_signing(json: Dict[str, Any]) -> str:
    """
    Encode a transaction and prepare for signing.

    Args:
        json: JSON object representing the transaction.

    Returns:
        A hex string of the encoded transaction.
    """
    return cast(
        str,
        _serialize_json(json, prefix=_TRANSACTION_SIGNATURE_PREFIX, signing_only=True),
    )


def encode_for_signing_claim(json: Dict[str, Any]) -> str:
    """
    Encode a transaction and prepare for signing with a claim.

    Args:
        json: JSON object representing the transaction.

    Returns:
        A hex string of the encoded transaction.
    """
    prefix = _PAYMENT_CHANNEL_CLAIM_PREFIX
    channel = Hash256.from_value(json["channel"])
    amount = UInt64.from_value(int(json["amount"]))

    buffer = prefix + bytes(channel) + bytes(amount)
    return buffer.hex().upper()


def encode_for_multisigning(json: Dict[str, Any], signing_account: str) -> str:
    """
    Encode a transaction and prepare for multi-signing.

    Args:
        json: JSON object representing the transaction.
        signing_account: string representing the account to sign the transaction with.

    Returns:
        A hex string of the encoded transaction.
    """
    assert json["SigningPubKey"] == ""
    signing_account_id = bytes(AccountID.from_value(signing_account))

    return cast(
        str,
        _serialize_json(
            json,
            prefix=_TRANSACTION_MULTISIG_PREFIX,
            suffix=signing_account_id,
            signing_only=True,
        ),
    )


def decode(buffer: str) -> Dict[str, Any]:
    """
    Decode a transaction.

    Args:
        buffer: a hex-string of the encoded transaction.

    Returns:
        The JSON representation of the transaction.
    """
    parser = BinaryParser(buffer)
    parsed_type = cast(SerializedDict, parser.read_type(SerializedDict))
    return parsed_type.to_json()


def _serialize_json(
    json: Dict[str, Any],
    prefix: Optional[bytes] = None,
    suffix: Optional[bytes] = None,
    signing_only: bool = False,
) -> bytes:
    buffer = b""
    if prefix is not None:
        buffer += prefix

    buffer += bytes(SerializedDict.from_value(json, signing_only))

    if suffix is not None:
        buffer += suffix

    return cast(bytes, buffer.hex().upper())
