"""
Codec for serializing and deserializing a hash field with a width
of 256 bits (32 bytes).
`See Hash Fields <https://xrpl.org/serialization.html#hash-fields>`_
"""
from __future__ import annotations

from typing import Type

from typing_extensions import Final

from xrpl.binarycodec.types.hash import Hash


class Hash256(Hash):
    """
    Codec for serializing and deserializing a hash field with a width
    of 256 bits (32 bytes).
    `See Hash Fields <https://xrpl.org/serialization.html#hash-fields>`_


    Attributes:
        _LENGTH: The length of this hash in bytes.
    """

    _LENGTH: Final[int] = 32

    @classmethod
    def _get_length(cls: Type[Hash256]) -> int:
        return cls._LENGTH
