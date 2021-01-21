"""Derived UInt class for serializing/deserializing 8 bit UInt."""
from xrpl.binary_codec.exceptions import XRPLBinaryCodecException
from xrpl.binary_codec.types import UInt

_width = 8 / 8


class UInt8(UInt):
    """Derived UInt class for serializing/deserializing 8 bit UInt."""

    def __init__(self, uint_bytes):
        super().__init__(uint_bytes)

    @property
    def value(self):
        pass

    @staticmethod
    def from_parser(parser):
        return UInt8(parser.read(_width))

    @staticmethod
    def from_value(value):
        if isinstance(value, UInt8):
            return value

        if isinstance(value, int):
            return UInt8(bytes([value]))

        raise XRPLBinaryCodecException("Cannot construct UInt8 from given value")


DEFAULT_UINT8 = UInt8(bytes([_width]))
