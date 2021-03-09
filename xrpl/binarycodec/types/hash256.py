"""
Codec for serializing and deserializing a hash field with a width
of 256 bits (32 bytes).
`See Hash Fields <https://xrpl.org/serialization.html#hash-fields>`_
"""
from __future__ import annotations

from typing import Optional, Type

from xrpl.binarycodec import XRPLBinaryCodecException
from xrpl.binarycodec.binary_wrappers.binary_parser import BinaryParser
from xrpl.binarycodec.types.hash import Hash

_LENGTH = 32


class Hash256(Hash):
    """
    Codec for serializing and deserializing a hash field with a width
    of 256 bits (32 bytes).
    `See Hash Fields <https://xrpl.org/serialization.html#hash-fields>`_
    """

    @classmethod
    def from_value(cls: Type[Hash256], value: str) -> Hash256:
        """
        Construct a Hash256 object from a hex string.

        Args:
            value: The string to construct a Hash256 object from.

        Returns:
            The Hash256 constructed from value.

        Raises:
            XRPLBinaryCodecException: If the supplied value is of the wrong type.
        """
        if not isinstance(value, str):
            raise XRPLBinaryCodecException(
                "Invalid type to construct a Hash256: expected str,"
                " received {}.".format(value.__class__.__name__)
            )
        return cls(bytes.fromhex(value))

    @classmethod
    def from_parser(
        cls: Type[Hash256], parser: BinaryParser, length_hint: Optional[int] = None
    ) -> Hash256:
        """
        Construct a Hash256 object from an existing BinaryParser.

        Args:
            parser: The parser to construct a Hash256 from.
            length_hint: The number of bytes to consume from the parser.

        Returns:
            The Hash256 constructed from parser.
        """
        num_bytes = length_hint if length_hint is not None else cls._get_length()
        return cls(parser.read(num_bytes))

    @classmethod
    def _get_length(cls: Type[Hash]) -> int:
        return _LENGTH
