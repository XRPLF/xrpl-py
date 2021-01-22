"""Derived UInt class for serializing/deserializing 64 bit UInt."""
from xrpl.binary_codec.exceptions import XRPLBinaryCodecException
from xrpl.binary_codec.types import UInt

_WIDTH = 8  # 64 / 8


class UInt64(UInt):
    """Derived UInt class for serializing/deserializing 64 bit UInt."""

    def __init__(self, buffer):
        """Construct a new UInt64 type from a `bytes` value."""
        if buffer is None:
            super().__init__(DEFAULT_UINT64.buffer)
        else:
            super().__init__(buffer)

    @property
    def value(self):
        """Get the value of the UInt64 represented by `self.buffer`."""
        return self.buffer[:_WIDTH]

    @classmethod
    def from_parser(cls, parser):
        """Construct a new UInt64 type from a BinaryParser."""
        return cls(parser.read(_WIDTH))

    @classmethod
    def from_value(cls, value):
        """Construct a new UInt64 type from a number."""
        if isinstance(value, int):
            value_bytes = (value).to_bytes(_WIDTH, byteorder="big")
            return cls(value_bytes)

        raise XRPLBinaryCodecException("Cannot construct UInt64 from given value")


DEFAULT_UINT64 = UInt64(bytes(_WIDTH))
