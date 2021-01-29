"""A hash field with a width of 160 bits (20 bytes).
`See Hash Fields <https://xrpl.org/serialization.html#hash-fields>`_
"""
from __future__ import annotations

from typing import Optional

from xrpl.binary_codec.binary_wrappers.binary_parser import BinaryParser
from xrpl.binary_codec.types.hash import Hash


class Hash160(Hash):
    """
    A hash field with a width of 160 bits (20 bytes).
    `See Hash Fields <https://xrpl.org/serialization.html#hash-fields>`_


    Attributes:
        width: The length of this hash in bytes.
    """

    _width = 20

    def __init__(self: Hash160, buffer: bytes = None) -> None:
        """Construct a Hash160."""
        buffer = buffer if buffer is not None else bytes(self._width)
        super().__init__(buffer)

    @classmethod
    def from_value(cls: Hash160, value: str) -> Hash160:
        """
        Construct a Hash160 object from a hex string.

        Args:
            value: The string to construct a Hash160 from.

        Returns:
            The Hash160 constructed from value.
        """
        return cls(bytes.fromhex(value))

    @classmethod
    def from_parser(
        cls: Hash160, parser: BinaryParser, length_hint: Optional[int] = None
    ) -> Hash160:
        """
        Construct a Hash160 object from an existing BinaryParser.

        Args:
            parser: The parser to construct Hash160 from.
            length_hint: A hint for the parser.

        Returns:
            The Hash160 constructed from parser.
        """
        num_bytes = length_hint if length_hint is not None else cls._width
        return cls(parser.read(num_bytes))
