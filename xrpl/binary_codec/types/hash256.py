"""A hash field with a width of 256 bits (32 bytes).
`See Hash Fields <https://xrpl.org/serialization.html#hash-fields>`_
"""
from __future__ import annotations

from typing import Optional

from xrpl.binary_codec.binary_wrappers.binary_parser import BinaryParser
from xrpl.binary_codec.types.hash import Hash


class Hash256(Hash):
    """
    A hash field with a width of 256 bits (32 bytes).
    `See Hash Fields <https://xrpl.org/serialization.html#hash-fields>`_


    Attributes:
        width: The length of this hash in bytes.
    """

    _width = 32

    def __init__(self: Hash256, buffer: bytes = None) -> None:
        """Construct a Hash256."""
        buffer = buffer if buffer is not None else bytes(self._width)
        super().__init__(buffer)

    @classmethod
    def from_value(cls: Hash256, value: str) -> Hash256:
        """Construct a Hash256 object from a hex string."""
        return cls(bytes.fromhex(value))

    @classmethod
    def from_parser(
        cls: Hash256, parser: BinaryParser, length_hint: Optional[int] = None
    ) -> Hash256:
        """Construct a Hash256 object from an existing BinaryParser."""
        num_bytes = length_hint if length_hint is not None else cls._width
        return cls(parser.read(num_bytes))
