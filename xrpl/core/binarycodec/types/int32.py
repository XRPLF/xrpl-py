"""Class for serializing and deserializing a signed 32-bit integer."""

from __future__ import annotations

from typing import Optional, Type, Union

from typing_extensions import Final, Self

from xrpl.core.binarycodec.binary_wrappers.binary_parser import BinaryParser
from xrpl.core.binarycodec.exceptions import XRPLBinaryCodecException
from xrpl.core.binarycodec.types.serialized_type import SerializedType

_WIDTH: Final[int] = 4  # 32 / 8


class Int32(SerializedType):
    """Class for serializing and deserializing a signed 32-bit integer."""

    def __init__(self: Self, buffer: bytes = bytes(_WIDTH)) -> None:
        """Construct a new Int32 type from a ``bytes`` value."""
        super().__init__(buffer)

    @property
    def value(self: Self) -> int:
        """Get the value of the Int32 represented by `self.buffer`."""
        return int.from_bytes(self.buffer, byteorder="big", signed=True)

    @classmethod
    def from_parser(
        cls: Type[Self], parser: BinaryParser, _length_hint: Optional[int] = None
    ) -> Self:
        """Construct a new Int32 type from a BinaryParser."""
        return cls(parser.read(_WIDTH))

    @classmethod
    def from_value(cls: Type[Self], value: int) -> Self:
        """Construct a new Int32 type from an integer."""
        if not isinstance(value, int):
            raise XRPLBinaryCodecException(
                f"Invalid type to construct Int32: expected int, "
                f"received {value.__class__.__name__}."
            )
        return cls(value.to_bytes(_WIDTH, byteorder="big", signed=True))

    def to_json(self: Self) -> int:
        """Convert the Int32 to JSON (returns the integer value)."""
        return self.value

    def __eq__(self: Self, other: object) -> bool:
        """Determine whether two Int32 objects are equal."""
        if isinstance(other, int):
            return self.value == other
        if isinstance(other, Int32):
            return self.value == other.value
        return NotImplemented

    def __lt__(self: Self, other: object) -> bool:
        """Determine whether this Int32 is less than another."""
        if isinstance(other, int):
            return self.value < other
        if isinstance(other, Int32):
            return self.value < other.value
        return NotImplemented

    def __gt__(self: Self, other: object) -> bool:
        """Determine whether this Int32 is greater than another."""
        if isinstance(other, int):
            return self.value > other
        if isinstance(other, Int32):
            return self.value > other.value
        return NotImplemented
