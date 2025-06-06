"""
Codec for encoding objects into the XRP Ledger's canonical binary format and
decoding them.
"""

from typing import Any, Dict, List, Optional, TypedDict, cast

from typing_extensions import Final

from xrpl.core.binarycodec.binary_wrappers.binary_parser import BinaryParser
from xrpl.core.binarycodec.types import AccountID, Hash256, STObject, UInt32, UInt64


def _num_to_bytes(num: int) -> bytes:
    return (num).to_bytes(4, byteorder="big", signed=False)


_TRANSACTION_SIGNATURE_PREFIX: Final[bytes] = _num_to_bytes(0x53545800)
_PAYMENT_CHANNEL_CLAIM_PREFIX: Final[bytes] = _num_to_bytes(0x434C4D00)
_TRANSACTION_MULTISIG_PREFIX: Final[bytes] = _num_to_bytes(0x534D5400)
_BATCH_PREFIX: Final[bytes] = _num_to_bytes(0x42434800)


def encode(json: Dict[str, Any]) -> str:
    """
    Encode a transaction or other object into the canonical binary format.

    Args:
        json: A JSON-like dictionary representation of an object.

    Returns:
        The binary-encoded object, as a hexadecimal string.
    """
    return _serialize_json(json)


def encode_for_signing(json: Dict[str, Any]) -> str:
    """
    Encode a transaction into binary format in preparation for signing. (Only
    encodes fields that are intended to be signed.)

    Args:
        json: A JSON-like dictionary representation of a transaction.

    Returns:
        The binary-encoded transaction, ready to be signed.
    """
    return _serialize_json(
        json,
        prefix=_TRANSACTION_SIGNATURE_PREFIX,
        signing_only=True,
    )


def encode_for_signing_claim(json: Dict[str, Any]) -> str:
    """
    Encode a `payment channel <https://xrpl.org/payment-channels.html>`_ Claim
    to be signed.

    Args:
        json: A JSON-like dictionary representation of a Claim.

    Returns:
        The binary-encoded claim, ready to be signed.
    """
    prefix = _PAYMENT_CHANNEL_CLAIM_PREFIX
    channel = Hash256.from_value(json["channel"])
    amount = UInt64.from_value(int(json["amount"]))

    buffer = prefix + bytes(channel) + bytes(amount)
    return buffer.hex().upper()


class BatchSigningDict(TypedDict):
    """
    A TypedDict for the JSON representation of a Batch transaction that is
    intended to be signed.
    """

    flags: int
    transaction_ids: List[str]


def encode_for_signing_batch(json: BatchSigningDict) -> str:
    """
    Encode a Batch transaction's data to be signed.

    Args:
        json: A JSON-like dictionary representation of Batch data.

    Returns:
        The binary-encoded Batch data, ready to be signed.
    """
    prefix = _BATCH_PREFIX
    flags = UInt32.from_value(json["flags"])
    transaction_ids = json["transaction_ids"]
    len_transaction_ids = UInt32.from_value(len(transaction_ids))

    buffer = prefix + bytes(flags) + bytes(len_transaction_ids)
    for tx in transaction_ids:
        buffer += bytes(Hash256.from_value(tx))

    return buffer.hex().upper()


def encode_for_multisigning(json: Dict[str, Any], signing_account: str) -> str:
    """
    Encode a transaction into binary format in preparation for providing one
    signature towards a multi-signed transaction.
    (Only encodes fields that are intended to be signed.)

    Args:
        json: A JSON-like dictionary representation of a transaction.
        signing_account: The address of the signer who'll provide the signature.

    Returns:
        A hex string of the encoded transaction.
    """
    signing_account_id = bytes(AccountID.from_value(signing_account))

    return _serialize_json(
        json,
        prefix=_TRANSACTION_MULTISIG_PREFIX,
        suffix=signing_account_id,
        signing_only=True,
    )


def decode(buffer: str) -> Dict[str, Any]:
    """
    Decode a transaction from binary format to a JSON-like dictionary
    representation.

    Args:
        buffer: The encoded transaction binary, as a hexadecimal string.

    Returns:
        A JSON-like dictionary representation of the transaction.
    """
    parser = BinaryParser(buffer)
    parsed_type = cast(STObject, parser.read_type(STObject))
    return parsed_type.to_json()


def _serialize_json(
    json: Dict[str, Any],
    prefix: Optional[bytes] = None,
    suffix: Optional[bytes] = None,
    signing_only: bool = False,
) -> str:
    buffer = b""
    if prefix is not None:
        buffer += prefix

    buffer += bytes(STObject.from_value(json, signing_only))

    if suffix is not None:
        buffer += suffix

    return buffer.hex().upper()
