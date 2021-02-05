"""High-level binary codec methods."""

from decimal import Decimal
from typing import Any, Dict, List, Optional, Union

from xrpl.binary_codec.binary_wrappers.binary_parser import BinaryParser
from xrpl.binary_codec.types.account_id import AccountID
from xrpl.binary_codec.types.hash256 import Hash256
from xrpl.binary_codec.types.serialized_transaction import SerializedTransaction
from xrpl.binary_codec.types.uint64 import UInt64


def _num_to_bytes(num: int) -> bytes:
    return (num).to_bytes(4, byteorder="big", signed=False)


_TRANSACTION_SIGNATURE_PREFIX = _num_to_bytes(0x53545800)
_PAYMENT_CHANNEL_CLAIM_PREFIX = _num_to_bytes(0x434C4D00)
_TRANSACTION_MULTISIG_PREFIX = _num_to_bytes(0x534D5400)


def encode(json: Union[List[Any], Dict[str, Any]]) -> str:
    """
    Encode a transaction.

    Args:
        json: the JSON representation of a transaction.

    Returns:
        A hex-string of the encoded transaction.
    """
    return _serialize_json(json)


def encode_for_signing(json: Union[List[Any], Dict[str, Any]]) -> str:
    """
    Encode a transaction and prepare for signing.

    Args:
        json: JSON object representing the transaction.

    Returns:
        A hex string of the encoded transaction.
    """
    return _serialize_json(
        json, prefix=_TRANSACTION_SIGNATURE_PREFIX, signing_only=True
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

    buffer = prefix + channel.to_bytes() + amount.to_bytes()
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
    signing_account_id = AccountID.from_value(signing_account).to_bytes()

    return _serialize_json(
        json,
        prefix=_TRANSACTION_MULTISIG_PREFIX,
        suffix=signing_account_id,
        signing_only=True,
    )


def decode(buffer: str) -> Union[List[Any], Dict[str, Any]]:
    """
    Decode a transaction.

    Args:
        buffer: a hex-string of the encoded transaction.

    Returns:
        The JSON representation of the transaction.
    """
    parser = BinaryParser(buffer)
    return parser.read_type(SerializedTransaction).to_json()


def encode_quality(quality: str) -> str:
    """
    Encode a quality value.

    Args:
        quality: A string representation of a number.

    Return:
        A hex-string representing the quality.
    """
    decimal = Decimal(quality)
    exponent = decimal.adjusted() - 15
    quality_int = int((decimal * Decimal("1e{}".format(-1 * exponent))).copy_abs())
    buffer = bytearray(UInt64.from_value(quality_int).to_bytes())
    buffer[0] = exponent + 100
    return buffer.hex().upper()


def decode_quality(quality: str) -> str:
    """
    Decode a quality value.

    Args:
        quality: A hex-string of a quality.

    Returns:
        A string representing the quality.
    """
    buffer = bytes.fromhex(quality)[-8:]
    exponent = buffer[0] - 100
    mantissa = Decimal(str(int(buffer[1:].hex(), 16)))
    return str(mantissa * Decimal("1e{}".format(exponent)))


def _serialize_json(
    json: Union[List[Any], Dict[str, Any]],
    prefix: Optional[bytes] = None,
    suffix: Optional[bytes] = None,
    signing_only: bool = False,
) -> bytes:
    buffer = b""
    if prefix is not None:
        buffer += prefix

    buffer += SerializedTransaction.from_value(json, signing_only).to_bytes()

    if suffix is not None:
        buffer += suffix

    return buffer.hex().upper()
