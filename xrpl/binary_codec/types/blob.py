"""Variable length encoded type."""

from __future__ import annotations

from typing import Optional

from xrpl.binary_codec.binary_wrappers.binary_parser import BinaryParser
from xrpl.binary_codec.exceptions import XRPLBinaryCodecException
from xrpl.binary_codec.types.serialized_type import SerializedType


class Blob(SerializedType):
    """Variable length encoded type."""

    def __init__(self: Blob, buffer: bytes) -> None:
        """Construct a new Blob type from a `bytes` value."""
        super().__init__(buffer)

    @classmethod
    def from_parser(
        cls: Blob, parser: BinaryParser, length_hint: Optional[int] = None
    ) -> Blob:
        """
        Defines how to read a Blob from a BinaryParser.

        Args:
            parser: The parser to construct a Blob from.
            length_hint: A hint for the parser.

        Returns:
            The Blob constructed from parser.
        """
        return cls(parser.read(length_hint))

    @classmethod
    def from_value(cls: Blob, value: str) -> Blob:
        """
        Create a Blob object from a hex-string.

        Args:
            value: The string to construct a Blob from.

        Returns:
            The Blob constructed from value.

        Raises:
            XRPLBinaryCodecException: If the Blob can't be constructed from value.
        """
        if isinstance(value, str):
            return cls(bytes.fromhex(value))

        raise XRPLBinaryCodecException("Cannot construct Blob from value given")
