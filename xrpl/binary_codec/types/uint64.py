"""Derived UInt class for serializing/deserializing 64 bit UInt."""
from __future__ import annotations

import re
from typing import Union

from xrpl.binary_codec.binary_wrappers.binary_parser import BinaryParser
from xrpl.binary_codec.exceptions import XRPLBinaryCodecException
from xrpl.binary_codec.types.uint import UInt

_WIDTH = 8  # 64 / 8

_HEX_REGEX = re.compile("^[A-F0-9]{16}$")


class UInt64(UInt):
    """Derived UInt class for serializing/deserializing 64 bit UInt."""

    def __init__(self: UInt64, buffer: bytes = bytes(_WIDTH)) -> None:
        """Construct a new UInt64 type from a `bytes` value."""
        super().__init__(buffer)

    @classmethod
    def from_parser(cls: UInt64, parser: BinaryParser) -> UInt64:
        """
        Construct a new UInt64 type from a BinaryParser.

        Args:
            parser: The BinaryParser to construct a UInt64 from.

        Returns:
            The UInt64 constructed from parser.
        """
        return cls(parser.read(_WIDTH))

    @classmethod
    def from_value(cls: UInt64, value: Union[str, int]) -> UInt64:
        """
        Construct a new UInt64 type from a number.

        Args:
            value: The number to construct a UInt64 from.

        Returns:
            The UInt64 constructed from value.

        Raises:
            XRPLBinaryCodecException: If a UInt64 could not be constructed from value.
        """
        if isinstance(value, int):
            if value < 0:
                raise XRPLBinaryCodecException(
                    "{} must be an unsigned integer".format(value)
                )
            value_bytes = (value).to_bytes(_WIDTH, byteorder="big", signed=False)
            return cls(value_bytes)

        if isinstance(value, str):
            if not _HEX_REGEX.fullmatch(value):
                raise XRPLBinaryCodecException("{} is not a valid hex string")
            value_bytes = bytes.fromhex(value)
            return cls(value_bytes)

        raise XRPLBinaryCodecException(
            "Cannot construct UInt64 from given value {}".format(value)
        )
