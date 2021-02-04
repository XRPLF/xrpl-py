"""Codec for serializing and deserializing a hash field with a width
of 128 bits (16 bytes).
`See Hash Fields <https://xrpl.org/serialization.html#hash-fields>`_
"""
from __future__ import annotations

from typing import Optional

from xrpl.binarycodec import XRPLBinaryCodecException
from xrpl.binarycodec.binary_wrappers.binary_parser import BinaryParser
from xrpl.binarycodec.types.hash import Hash


class Hash128(Hash):
    """
    Codec for serializing and deserializing a hash field with a width
    of 128 bits (16 bytes).
    `See Hash Fields <https://xrpl.org/serialization.html#hash-fields>`_


    Attributes:
        width: The length of this hash in bytes.
    """

    _WIDTH = 16

    def __init__(self: Hash128, buffer: bytes = None) -> None:
        """Construct a Hash128."""
        buffer = buffer if buffer is not None else bytes(self._width)
        super().__init__(buffer)

    @classmethod
    def from_value(cls: Hash128, value: str) -> Hash128:
        """
        Construct a Hash128 object from a hex string.

        Args:
            value: The value to construct a Hash128 from.

        Returns:
            The Hash128 object constructed from value.

        Raises:
            XRPLBinaryCodecException: If the supplied value is of the wrong type.
        """
        if not isinstance(value, str):
            raise XRPLBinaryCodecException("Invalid type to construct a Hash128")

        return cls(bytes.fromhex(value))

    @classmethod
    def from_parser(
        cls: Hash128, parser: BinaryParser, length_hint: Optional[int] = None
    ) -> Hash128:
        """
        Construct a Hash128 object from an existing BinaryParser.

        Args:
            parser: The parser to construct the Hash128 object from.
            length_hint: The number of bytes to consume from the parser.

        Returns:
            The Hash128 object constructed from a parser.
        """
        num_bytes = length_hint if length_hint is not None else cls._width
        return cls(parser.read(num_bytes))
