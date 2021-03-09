"""
Codec for serializing and deserializing a hash field with a width
of 128 bits (16 bytes).
`See Hash Fields <https://xrpl.org/serialization.html#hash-fields>`_
"""
from __future__ import annotations

from typing import Optional, Type

from xrpl.binarycodec import XRPLBinaryCodecException
from xrpl.binarycodec.binary_wrappers.binary_parser import BinaryParser
from xrpl.binarycodec.types.hash import Hash

_LENGTH = 16


class Hash128(Hash):
    """
    Codec for serializing and deserializing a hash field with a width
    of 128 bits (16 bytes).
    `See Hash Fields <https://xrpl.org/serialization.html#hash-fields>`_
    """

    @classmethod
    def from_value(cls: Type[Hash128], value: str) -> Hash128:
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
            raise XRPLBinaryCodecException(
                "Invalid type to construct a Hash128: expected str,"
                " received {}.".format(value.__class__.__name__)
            )

        return cls(bytes.fromhex(value))

    @classmethod
    def from_parser(
        cls: Type[Hash128], parser: BinaryParser, length_hint: Optional[int] = None
    ) -> Hash128:
        """
        Construct a Hash128 object from an existing BinaryParser.

        Args:
            parser: The parser to construct the Hash128 object from.
            length_hint: The number of bytes to consume from the parser.

        Returns:
            The Hash128 object constructed from a parser.
        """
        num_bytes = length_hint if length_hint is not None else cls._get_length()
        return cls(parser.read(num_bytes))

    @classmethod
    def _get_length(cls: Type[Hash]) -> int:
        return _LENGTH
