"""Class for serializing and deserializing a 32-bit UInt.
See `UInt Fields <https://xrpl.org/serialization.html#uint-fields>`_
"""
from __future__ import annotations

from typing import Union

from xrpl.binarycodec.binary_wrappers.binary_parser import BinaryParser
from xrpl.binarycodec.exceptions import XRPLBinaryCodecException
from xrpl.binarycodec.types.uint import UInt

_WIDTH = 4  # 32 / 8


class UInt32(UInt):
    """Class for serializing and deserializing a 32-bit UInt.
    See `UInt Fields <https://xrpl.org/serialization.html#uint-fields>`_
    """

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
    def from_value(cls: UInt32, value: Union[str, int]) -> UInt32:
        """
        Construct a new UInt32 type from a number.

        Args:
            value: The number to construct a UInt32 from.

        Returns:
            The UInt32 constructed from value.

        Raises:
            XRPLBinaryCodecException: If a UInt32 could not be constructed from value.
        """
        if not isinstance(value, (str, int)):
            raise XRPLBinaryCodecException("Invalid type to construct a UInt32")

        if isinstance(value, int):
            value_bytes = (value).to_bytes(_WIDTH, byteorder="big", signed=False)
            return cls(value_bytes)

        if isinstance(value, str) and value.isdigit():
            value_bytes = (int(value)).to_bytes(_WIDTH, byteorder="big", signed=False)
            return cls(value_bytes)

        raise XRPLBinaryCodecException("Cannot construct UInt32 from given value")
