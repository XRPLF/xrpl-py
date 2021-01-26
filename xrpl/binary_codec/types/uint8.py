"""Derived UInt class for serializing/deserializing 8 bit UInt."""
from xrpl.binary_codec.exceptions import XRPLBinaryCodecException
from xrpl.binary_codec.types import UInt

_WIDTH = 1  # 8 / 8


class UInt8(UInt):
    """Derived UInt class for serializing/deserializing 8 bit UInt."""

    def __init__(self, buffer):
        """Construct a new UInt8 type from a `bytes` value."""
        if buffer is None:
            super().__init__(bytes(_WIDTH))
        else:
            super().__init__(buffer)

    @classmethod
    def from_parser(cls, parser):
        """Construct a new UInt8 type from a BinaryParser."""
        return cls(parser.read(_WIDTH))

    @classmethod
    def from_value(cls, value):
        """Construct a new UInt8 type from a number."""
        if isinstance(value, int):
            value_bytes = (value).to_bytes(_WIDTH, byteorder="big")
            return cls(value_bytes)

        raise XRPLBinaryCodecException("Cannot construct UInt8 from given value")
