"""Codec for serializing and deserializing sidechain fields."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, Type, Union

from xrpl.core.binarycodec.binary_wrappers.binary_parser import BinaryParser
from xrpl.core.binarycodec.exceptions import XRPLBinaryCodecException
from xrpl.core.binarycodec.types.account_id import AccountID
from xrpl.core.binarycodec.types.issued_currency import IssuedCurrency
from xrpl.core.binarycodec.types.serialized_type import SerializedType
from xrpl.models.sidechain import Sidechain as SidechainModel

_TYPE_ORDER: List[Tuple[str, Type[SerializedType]]] = [
    ("src_chain_door", AccountID),
    ("src_chain_issue", IssuedCurrency),
    ("dst_chain_door", AccountID),
    ("dst_chain_issue", IssuedCurrency),
]


class Sidechain(SerializedType):
    """Codec for serializing and deserializing sidechain fields."""

    def __init__(self: Sidechain, buffer: bytes) -> None:
        """Construct an Sidechain from given bytes."""
        super().__init__(buffer)

    @classmethod
    def from_value(
        cls: Type[Sidechain], value: Union[str, Dict[str, str]]
    ) -> Sidechain:
        """
        Construct a Sidechain object from a dictionary representation of a sidechain.

        Args:
            value: The dictionary to construct a Sidechain object from.

        Returns:
            A Sidechain object constructed from value.

        Raises:
            XRPLBinaryCodecException: If the Sidechain representation is invalid.
        """
        if SidechainModel.is_dict_of_model(value):
            buffer = b""
            for (name, object_type) in _TYPE_ORDER:
                obj = object_type.from_value(value[name])
                buffer += bytes(obj)
            return cls(buffer)

        raise XRPLBinaryCodecException(
            "Invalid type to construct an Sidechain: expected dict,"
            f" received {value.__class__.__name__}."
        )

    @classmethod
    def from_parser(
        cls: Type[Sidechain], parser: BinaryParser, length_hint: Optional[int] = None
    ) -> Sidechain:
        """
        Construct a Sidechain object from an existing BinaryParser.

        Args:
            parser: The parser to construct the Sidechain object from.
            length_hint: The number of bytes to consume from the parser.

        Returns:
            The Sidechain object constructed from a parser.
        """
        buffer = b""

        for (_, object_type) in _TYPE_ORDER:
            obj = object_type.from_parser(parser)
            buffer += bytes(obj)

        return cls(buffer)

    def to_json(self: Sidechain) -> Union[str, Dict[Any, Any]]:
        """
        Returns the JSON representation of a sidechain.

        Returns:
            The JSON representation of a Sidechain.
        """
        parser = BinaryParser(str(self))
        return_json = {}
        for (name, object_type) in _TYPE_ORDER:
            obj = object_type.from_parser(parser)
            return_json[name] = obj.to_json()

        return return_json
