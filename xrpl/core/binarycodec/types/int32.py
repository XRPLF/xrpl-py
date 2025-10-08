"""Class for serializing and deserializing a 32-bit Int.
See `UInt Fields <https://xrpl.org/serialization.html#uint-fields>`_
"""

from __future__ import annotations

from typing import Optional, Type, Union

from typing_extensions import Final, Self

from xrpl.core.binarycodec.binary_wrappers.binary_parser import BinaryParser
from xrpl.core.binarycodec.exceptions import XRPLBinaryCodecException
from xrpl.core.binarycodec.types.int import Int

_WIDTH: Final[int] = 4  # 32 / 8


class Int32(Int):
    """
    Class for serializing and deserializing a 32-bit Int.
    See `UInt Fields <https://xrpl.org/serialization.html#uint-fields>`_
    """

    def __init__(self: Self, buffer: bytes = bytes(_WIDTH)) -> None:
        """Construct a new Int32 type from a ``bytes`` value."""
        super().__init__(buffer)

    @classmethod
    def from_parser(
        cls: Type[Self], parser: BinaryParser, _length_hint: Optional[int] = None
    ) -> Self:
        """
        Construct a new Int32 type from a BinaryParser.

        Args:
            parser: A BinaryParser to construct a Int32 from.

        Returns:
            The Int32 constructed from parser.
        """
        return cls(parser.read(_WIDTH))

    @classmethod
    def from_value(cls: Type[Self], value: Union[str, int]) -> Self:
        """
        Construct a new Int32 type from a number.

        Args:
            value: The number to construct a Int32 from.

        Returns:
            The Int32 constructed from value.

        Raises:
            XRPLBinaryCodecException: If a Int32 could not be constructed from value.
        """
        if not isinstance(value, (str, int)):
            raise XRPLBinaryCodecException(
                "Invalid type to construct a Int32: expected str or int,"
                " received {value.__class__.__name__}."
            )

        if isinstance(value, int):
            value_bytes = (value).to_bytes(_WIDTH, byteorder="big", signed=True)
            return cls(value_bytes)

        if isinstance(value, str) and value.isdigit():
            value_bytes = (int(value)).to_bytes(_WIDTH, byteorder="big", signed=True)
            return cls(value_bytes)

        raise XRPLBinaryCodecException("Cannot construct Int32 from given value")
