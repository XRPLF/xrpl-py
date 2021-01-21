"""Derived UInt class for serializing/deserializing 8 bit UInt."""
from xrpl.binary_codec.exceptions import XRPLBinaryCodecException
from xrpl.binary_codec.types import UInt

_width = 8 / 8


class UInt8(UInt):
    """Derived UInt class for serializing/deserializing 8 bit UInt."""

    def __init__(self, uint_bytes):
        """Construct a new UInt8 type from a `bytes` value."""
        super().__init__(uint_bytes)

    @property
    def value(self):
        """Get the value of the UInt8 represented by `this.bytes`."""
        pass

    @classmethod
    def from_parser(cls, parser):
        """Construct a new UInt8 type from a binary parser."""
        return cls(parser.read(_width))

    @classmethod
    def from_value(cls, value):
        """Construct a new UInt8 type from a number."""
        if isinstance(value, cls):
            return value

        if isinstance(value, int):
            return cls(bytes([value]))

        raise XRPLBinaryCodecException("Cannot construct UInt8 from given value")


DEFAULT_UINT8 = UInt8(bytes([_width]))
