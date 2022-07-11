"""Codec for serializing and deserializing bridge fields."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, Type, Union, cast

from xrpl.core.binarycodec.binary_wrappers.binary_parser import BinaryParser
from xrpl.core.binarycodec.exceptions import XRPLBinaryCodecException
from xrpl.core.binarycodec.types.account_id import AccountID
from xrpl.core.binarycodec.types.issued_currency import IssuedCurrency
from xrpl.core.binarycodec.types.serialized_type import SerializedType
from xrpl.models.bridge import Bridge as BridgeModel

_TYPE_ORDER: List[Tuple[str, Type[SerializedType]]] = [
    ("src_chain_door", AccountID),
    ("src_chain_issue", IssuedCurrency),
    ("dst_chain_door", AccountID),
    ("dst_chain_issue", IssuedCurrency),
]


class Bridge(SerializedType):
    """Codec for serializing and deserializing bridge fields."""

    def __init__(self: Bridge, buffer: bytes) -> None:
        """Construct a Bridge from given bytes."""
        super().__init__(buffer)

    @classmethod
    def from_value(cls: Type[Bridge], value: Union[str, Dict[str, str]]) -> Bridge:
        """
        Construct a Bridge object from a dictionary representation of a bridge.

        Args:
            value: The dictionary to construct a Bridge object from.

        Returns:
            A Bridge object constructed from value.

        Raises:
            XRPLBinaryCodecException: If the Bridge representation is invalid.
        """
        if BridgeModel.is_dict_of_model(value):
            value = cast(Dict[str, Any], value)
            buffer = b""
            for (name, object_type) in _TYPE_ORDER:
                obj = object_type.from_value(value[name])
                buffer += bytes(obj)
            return cls(buffer)

        raise XRPLBinaryCodecException(
            "Invalid type to construct an Bridge: expected dict,"
            f" received {value.__class__.__name__}."
        )

    @classmethod
    def from_parser(
        cls: Type[Bridge], parser: BinaryParser, length_hint: Optional[int] = None
    ) -> Bridge:
        """
        Construct a Bridge object from an existing BinaryParser.

        Args:
            parser: The parser to construct the Bridge object from.
            length_hint: The number of bytes to consume from the parser.

        Returns:
            The Bridge object constructed from a parser.
        """
        buffer = b""

        for (_, object_type) in _TYPE_ORDER:
            obj = object_type.from_parser(parser, length_hint)
            buffer += bytes(obj)

        return cls(buffer)

    def to_json(self: Bridge) -> Union[str, Dict[Any, Any]]:
        """
        Returns the JSON representation of a bridge.

        Returns:
            The JSON representation of a Bridge.
        """
        parser = BinaryParser(str(self))
        return_json = {}
        for (name, object_type) in _TYPE_ORDER:
            obj = object_type.from_parser(parser, None)
            return_json[name] = obj.to_json()

        return return_json
