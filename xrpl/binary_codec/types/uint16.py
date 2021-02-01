"""Derived UInt class for serializing/deserializing 16 bit UInt."""
from __future__ import annotations

from xrpl.binary_codec.binary_wrappers.binary_parser import BinaryParser
from xrpl.binary_codec.exceptions import XRPLBinaryCodecException
from xrpl.binary_codec.types.uint import UInt

_WIDTH = 2  # 16 / 8


class UInt16(UInt):
    """Derived UInt class for serializing/deserializing 16 bit UInt."""

    def __init__(self: UInt16, buffer: bytes = bytes(_WIDTH)) -> None:
        """Construct a new UInt16 type from a `bytes` value."""
        super().__init__(buffer)

    @classmethod
    def from_parser(cls: UInt16, parser: BinaryParser) -> UInt16:
        """
        Construct a new UInt16 type from a BinaryParser.

        Args:
            parser: The BinaryParser to construct a UInt16 from.

        Returns:
            The UInt16 constructed from parser.
        """
        return cls(parser.read(_WIDTH))

    @classmethod
    def from_value(cls: UInt16, value: int) -> UInt16:
        """
        Construct a new UInt16 type from a number.

        Args:
            value: The value to consutrct a UInt16 from.

        Returns:
            The UInt16 constructed from value.

        Raises:
            XRPLBinaryCodecException: If a UInt16 can't be constructed from value.
        """
        if isinstance(value, int):
            value_bytes = (value).to_bytes(_WIDTH, byteorder="big", signed=False)
            return cls(value_bytes)

        raise XRPLBinaryCodecException("Cannot construct UInt16 from given value")
