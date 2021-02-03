"""TODO: docstring"""

from typing import Any, Dict, List, Optional, Union

from xrpl.binary_codec.binary_wrappers.binary_parser import BinaryParser
from xrpl.binary_codec.types.serialized_transaction import SerializedTransaction


def encode(json: Union[List[Any], Dict[str, Any]]) -> str:
    """TODO: docstring"""
    return _serialize_json(json).hex().upper()


def decode(buffer: str) -> Union[List[Any], Dict[str, Any]]:
    """TODO: docstring"""
    parser = BinaryParser(buffer)
    return parser.read_type(SerializedTransaction).to_json()


def _serialize_json(
    json: Union[List[Any], Dict[str, Any]],
    prefix: Optional[bytes] = None,
    suffix: Optional[bytes] = None,
    signing: bool = False,
) -> bytes:
    """TODO: docstring"""
    buffer = b""
    if prefix is not None:
        buffer += prefix

    buffer += SerializedTransaction.from_value(json).to_bytes()

    if suffix is not None:
        buffer += suffix

    return buffer
