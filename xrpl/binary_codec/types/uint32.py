"""Derived UInt class for serializing/deserializing 32 bit UInt."""
from __future__ import annotations

from xrpl.binary_codec.binary_wrappers.binary_parser import BinaryParser
from xrpl.binary_codec.exceptions import XRPLBinaryCodecException
from xrpl.binary_codec.types.uint import UInt

_WIDTH = 4  # 32 / 8


class UInt32(UInt):
    """Derived UInt class for serializing/deserializing 32 bit UInt."""

    def __init__(self: UInt32, buffer: bytes = bytes(_WIDTH)) -> None:
        """Construct a new UInt32 type from a `bytes` value."""
        super().__init__(buffer)

    @classmethod
    def from_parser(cls: UInt32, parser: BinaryParser) -> UInt32:
        """
        Construct a new UInt32 type from a BinaryParser.

        Args:
            parser: A BinaryParser to construct a UInt32 from.

        Returns:
            The UInt32 constructed from parser.
        """
        return cls(parser.read(_WIDTH))

    @classmethod
    def from_value(cls: UInt32, value: int) -> UInt32:
        """
        Construct a new UInt32 type from a number.

        Args:
            value: The number to construct a UInt32 from.

        Returns:
            The UInt32 constructed from value.

        Raises:
            XRPLBinaryCodecException: If a UInt32 could not be constructed from value.
        """
        if isinstance(value, int):
            value_bytes = (value).to_bytes(_WIDTH, byteorder="big", signed=False)
            return cls(value_bytes)

        raise XRPLBinaryCodecException("Cannot construct UInt32 from given value")
