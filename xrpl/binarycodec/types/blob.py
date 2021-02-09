"""Variable length encoded type."""

from __future__ import annotations

from xrpl.binarycodec.binary_wrappers.binary_parser import BinaryParser
from xrpl.binarycodec.exceptions import XRPLBinaryCodecException
from xrpl.binarycodec.types.serialized_type import SerializedType


class Blob(SerializedType):
    """Variable length encoded type."""

    def __init__(self: Blob, buffer: bytes) -> None:
        """Construct a new Blob type from a `bytes` value."""
        super().__init__(buffer)

    @classmethod
    def from_parser(cls: Blob, parser: BinaryParser, length_hint: int) -> Blob:
        """
        Defines how to read a Blob from a BinaryParser.

        Args:
            parser: The parser to construct a Blob from.
            length_hint: The number of bytes to consume from the parser.

        Returns:
            The Blob constructed from parser.
        """
        return cls(parser.read(length_hint))

    @classmethod
    def from_value(cls: Blob, value: str) -> Blob:
        """
        Create a Blob object from a hex-string.

        Args:
            value: The hex-encoded string to construct a Blob from.

        Returns:
            The Blob constructed from value.

        Raises:
            XRPLBinaryCodecException: If the Blob can't be constructed from value.
        """
        if isinstance(value, str):
            return cls(bytes.fromhex(value))

        raise XRPLBinaryCodecException("Cannot construct Blob from value given")
