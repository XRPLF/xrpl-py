"""Derived UInt class for serializing/deserializing 16 bit UInt."""
from __future__ import annotations

from xrpl.binary_codec.binary_wrappers.binary_parser import BinaryParser
from xrpl.binary_codec.exceptions import XRPLBinaryCodecException
from xrpl.binary_codec.types.uint import UInt

_WIDTH = 2  # 16 / 8


class UInt16(UInt):
    """Derived UInt class for serializing/deserializing 16 bit UInt."""

    def __init__(self, buffer: bytes = bytes(_WIDTH)):
        """Construct a new UInt16 type from a `bytes` value."""
        super().__init__(buffer)

    @classmethod
    def from_parser(cls, parser: BinaryParser) -> UInt16:
        """Construct a new UInt16 type from a BinaryParser."""
        return cls(parser.read(_WIDTH))

    @classmethod
    def from_value(cls, value: int) -> UInt16:
        """Construct a new UInt16 type from a number."""
        if isinstance(value, int):
            value_bytes = (value).to_bytes(_WIDTH, byteorder="big", signed=False)
            return cls(value_bytes)

        raise XRPLBinaryCodecException("Cannot construct UInt16 from given value")
