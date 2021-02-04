"""High-level binary codec methods."""

from typing import Any, Dict, List, Optional, Union

from xrpl.binarycodec.binary_wrappers.binary_parser import BinaryParser
from xrpl.binarycodec.types.serialized_transaction import SerializedTransaction


def encode(json: Union[List[Any], Dict[str, Any]]) -> str:
    """
    Encode a transaction.

    Args:
        json: the JSON representation of a transaction.

    Returns:
        A hex-string of the encoded transaction.
    """
    return _serialize_json(json).hex().upper()


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


def _serialize_json(
    json: Union[List[Any], Dict[str, Any]],
    prefix: Optional[bytes] = None,
    suffix: Optional[bytes] = None,
    signing: bool = False,
) -> bytes:
    buffer = b""
    if prefix is not None:
        buffer += prefix

    buffer += SerializedTransaction.from_value(json).to_bytes()

    if suffix is not None:
        buffer += suffix

    return buffer
