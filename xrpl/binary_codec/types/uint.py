"""Base class for serializing and deserializing unsigned integers."""
from __future__ import annotations

from abc import ABC
from typing import Union

from xrpl.binary_codec.exceptions import XRPLBinaryCodecException


class UInt(ABC):
    """Base class for serializing and deserializing unsigned integers."""

    def __init__(self, buffer: bytes):
        """Construct a new UInt type from a `bytes` value."""
        self.buffer = buffer

    @property
    def value(self) -> int:
        """Get the value of the UInt represented by `self.buffer`."""
        return int.from_bytes(self.buffer, byteorder="big", signed=False)

    def __eq__(self, other: object) -> bool:
        """Determine whether two UInt objects are equal."""
        if isinstance(other, int):
            return self.value == other
        if isinstance(other, UInt):
            return self.value == other.value
        raise XRPLBinaryCodecException("Cannot compare UInt and {}".format(type(other)))

    def __ne__(self, other: object) -> bool:
        """Determine whether two UInt objects are unequal."""
        if isinstance(other, int):
            return self.value != other
        if isinstance(other, UInt):
            return self.value != other.value
        raise XRPLBinaryCodecException("Cannot compare UInt and {}".format(type(other)))

    def __lt__(self, other: object) -> bool:
        """Determine whether one UInt object is less than another."""
        if isinstance(other, int):
            return self.value < other
        if isinstance(other, UInt):
            return self.value < other.value
        raise XRPLBinaryCodecException("Cannot compare UInt and {}".format(type(other)))

    def __le__(self, other: object) -> bool:
        """Determine whether one UInt object is less than or equal to another."""
        if isinstance(other, int):
            return self.value <= other
        if isinstance(other, UInt):
            return self.value <= other.value
        raise XRPLBinaryCodecException("Cannot compare UInt and {}".format(type(other)))

    def __gt__(self, other: object) -> bool:
        """Determine whether one UInt object is greater than another."""
        if isinstance(other, int):
            return self.value > other
        if isinstance(other, UInt):
            return self.value > other.value
        raise XRPLBinaryCodecException("Cannot compare UInt and {}".format(type(other)))

    def __ge__(self, other: object) -> bool:
        """Determine whether one UInt object is greater than or equal to another."""
        if isinstance(other, int):
            return self.value >= other
        if isinstance(other, UInt):
            return self.value >= other.value
        raise XRPLBinaryCodecException("Cannot compare UInt and {}".format(type(other)))

    def to_json(self) -> Union[str, int]:
        """Convert a UInt object to JSON."""
        if isinstance(self.value, int):
            return self.value
        return str(self.value)
