"""Codec for serializing and deserializing bridge fields."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, Type, Union

from xrpl.core.binarycodec.binary_wrappers.binary_parser import BinaryParser
from xrpl.core.binarycodec.exceptions import XRPLBinaryCodecException
from xrpl.core.binarycodec.types.serialized_type import SerializedType
from xrpl.core.binarycodec.types.st_array import STArray
from xrpl.core.binarycodec.types.xchain_bridge import XChainBridge

_TYPE_ORDER: List[Tuple[str, Type[SerializedType]]] = [
    ("XChainBridge", XChainBridge),
    ("XChainClaimAttestationBatch", STArray),
    ("XChainCreateAccountAttestationBatch", STArray),
]

_TYPE_KEYS = {type[0] for type in _TYPE_ORDER}


class XChainAttestationBatch(SerializedType):
    """Codec for serializing and deserializing XChainAttestationBatch fields."""

    def __init__(self: XChainAttestationBatch, buffer: bytes) -> None:
        """Construct a XChainAttestationBatch from given bytes."""
        super().__init__(buffer)

    @classmethod
    def from_value(
        cls: Type[XChainAttestationBatch], value: Union[str, Dict[str, str]]
    ) -> XChainAttestationBatch:
        """
        Construct a XChainAttestationBatch object from a dictionary representation of a
        XChainAttestationBatch.

        Args:
            value: The dictionary to construct a XChainAttestationBatch object from.

        Returns:
            A XChainAttestationBatch object constructed from value.

        Raises:
            XRPLBinaryCodecException: If the XChainAttestationBatch representation is
                invalid.
        """
        if isinstance(value, dict) and set(value.keys()) == _TYPE_KEYS:
            buffer = b""
            for (name, object_type) in _TYPE_ORDER:
                obj = object_type.from_value(value[name])
                buffer += bytes(obj)
            return cls(buffer)

        raise XRPLBinaryCodecException(
            "Invalid type to construct an XChainAttestationBatch: expected dict,"
            f" received {value.__class__.__name__}."
        )

    @classmethod
    def from_parser(
        cls: Type[XChainAttestationBatch],
        parser: BinaryParser,
        length_hint: Optional[int] = None,
    ) -> XChainAttestationBatch:
        """
        Construct a XChainAttestationBatch object from an existing BinaryParser.

        Args:
            parser: The parser to construct the XChainAttestationBatch object from.
            length_hint: The number of bytes to consume from the parser.

        Returns:
            The XChainAttestationBatch object constructed from a parser.
        """
        buffer = b""

        for (_, object_type) in _TYPE_ORDER:
            obj = object_type.from_parser(parser, length_hint)
            buffer += bytes(obj)

        return cls(buffer)

    def to_json(self: XChainAttestationBatch) -> Union[str, Dict[Any, Any]]:
        """
        Returns the JSON representation of a XChainAttestationBatch.

        Returns:
            The JSON representation of a XChainAttestationBatch.
        """
        parser = BinaryParser(str(self))
        return_json = {}
        for (name, object_type) in _TYPE_ORDER:
            obj = object_type.from_parser(parser, None)
            return_json[name] = obj.to_json()

        return return_json
