"""
Class for serializing and deserializing a 64-bit UInt.
See `UInt Fields <https://xrpl.org/serialization.html#uint-fields>`_
"""
from __future__ import annotations

import re
from typing import Optional, Type, Union

from typing_extensions import Final

from xrpl.binarycodec.binary_wrappers.binary_parser import BinaryParser
from xrpl.binarycodec.exceptions import XRPLBinaryCodecException
from xrpl.binarycodec.types.uint import UInt

_WIDTH: Final[int] = 8  # 64 / 8

_HEX_REGEX: Final[re.Pattern[str]] = re.compile("^[A-F0-9]{16}$")


class UInt64(UInt):
    """
    Class for serializing and deserializing a 64-bit UInt.
    See `UInt Fields <https://xrpl.org/serialization.html#uint-fields>`_
    """

    def __init__(self: UInt64, buffer: bytes = bytes(_WIDTH)) -> None:
        """Construct a new UInt64 type from a `bytes` value."""
        super().__init__(buffer)

    @classmethod
    def from_parser(
        cls: Type[UInt64], parser: BinaryParser, length_hint: Optional[int] = None
    ) -> UInt64:
        """
        Construct a new UInt64 type from a BinaryParser.

        Args:
            parser: The BinaryParser to construct a UInt64 from.
            length_hint: The number of bytes to consume from the parser.

        Returns:
            The UInt64 constructed from parser.
        """
        return cls(parser.read(_WIDTH))

    @classmethod
    def from_value(cls: Type[UInt64], value: Union[str, int]) -> UInt64:
        """
        Construct a new UInt64 type from a number.

        Args:
            value: The number to construct a UInt64 from.

        Returns:
            The UInt64 constructed from value.

        Raises:
            XRPLBinaryCodecException: If a UInt64 could not be constructed from value.
        """
        if not isinstance(value, (str, int)):
            raise XRPLBinaryCodecException(
                "Invalid type to construct a UInt64: expected str or int,"
                " received {}.".format(value.__class__.__name__)
            )

        if isinstance(value, int):
            if value < 0:
                raise XRPLBinaryCodecException(
                    "{} must be an unsigned integer".format(value)
                )
            value_bytes = (value).to_bytes(_WIDTH, byteorder="big", signed=False)
            return cls(value_bytes)

        if isinstance(value, str):
            if not _HEX_REGEX.fullmatch(value):
                raise XRPLBinaryCodecException(
                    "{} is not a valid hex string".format(value)
                )
            value_bytes = bytes.fromhex(value)
            return cls(value_bytes)

        raise XRPLBinaryCodecException(
            "Cannot construct UInt64 from given value {}".format(value)
        )

    def to_json(self: UInt64) -> str:
        """
        Convert a UInt64 object to JSON (hex).

        Returns:
            The JSON representation of the UInt64 object.
        """
        return self.buffer.hex().upper()
