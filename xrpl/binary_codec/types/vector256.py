"""Codec for serializing and deserializing vectors of Hash256."""
from __future__ import annotations

from typing import List, Optional

from xrpl.binary_codec import XRPLBinaryCodecException
from xrpl.binary_codec.binary_wrappers.binary_parser import BinaryParser
from xrpl.binary_codec.types.hash256 import Hash256
from xrpl.binary_codec.types.serialized_type import SerializedType


class Vector256(SerializedType):
    """A vector of Hash256 objects."""

    def __init__(self, buffer: bytes) -> None:
        """Construct a Vector256."""
        super().__init__(buffer)

    @classmethod
    def from_value(cls, value: List[str]) -> Vector256:
        """Construct a Vector256 from a list of strings."""
        byte_list = []
        for string in value:
            byte_list.append(Hash256.from_value(string).to_bytes())
        return cls(b"".join(byte_list))

    @classmethod
    def from_parser(
        cls, parser: BinaryParser, length_hint: Optional[int] = None
    ) -> SerializedType:
        """Construct a Vector256 from a BinaryParser."""
        byte_list = []
        num_bytes = length_hint if length_hint is not None else len(parser)
        num_hashes = num_bytes // 32
        for i in range(num_hashes):
            byte_list.append(Hash256.from_parser(parser).to_bytes())
        return cls(b"".join(byte_list))

    def to_json(self) -> List[str]:
        """Return a list of hashes encoded as hex strings."""
        if len(self.buffer) % 32 != 0:
            raise XRPLBinaryCodecException("Invalid bytes for Vector256.")
        hash_list = []
        for i in range(0, len(self.buffer), 32):
            hash_list.append(self.buffer[i : i + 32].hex().upper())
        return hash_list
