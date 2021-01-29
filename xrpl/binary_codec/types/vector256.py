"""Codec for serializing and deserializing vectors of Hash256.
`See Hash Fields <https://xrpl.org/serialization.html#hash-fields>`_
"""
from __future__ import annotations

from typing import List, Optional

from xrpl.binary_codec.binary_wrappers.binary_parser import BinaryParser

# from xrpl.binary_codec.types.hash256 import Hash256
from xrpl.binary_codec.types.serialized_type import SerializedType


class Vector256(SerializedType):
    """A vector of Hash256 objects."""

    def __init__(self, buffer: bytes) -> None:
        """Construct a Vector256."""
        super().__init__(buffer)

    @classmethod
    def from_value(cls, value: List[str]) -> Vector256:
        """Construct a Vector256 from a list of strings."""
        pass

    @classmethod
    def from_parser(
        cls, parser: BinaryParser, length_hint: Optional[int] = None
    ) -> SerializedType:
        """Construct a Vector256 from a BinaryParser."""
        pass

    def to_json(self) -> str:
        """Return a list of hashes encoded as hex strings."""
        pass
