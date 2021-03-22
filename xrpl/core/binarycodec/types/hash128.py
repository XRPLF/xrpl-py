"""
Codec for serializing and deserializing a hash field with a width
of 128 bits (16 bytes).
`See Hash Fields <https://xrpl.org/serialization.html#hash-fields>`_
"""
from __future__ import annotations

from typing import Type

from xrpl.core.binarycodec.types.hash import Hash


class Hash128(Hash):
    """
    Codec for serializing and deserializing a hash field with a width
    of 128 bits (16 bytes).
    `See Hash Fields <https://xrpl.org/serialization.html#hash-fields>`_
    """

    @classmethod
    def _get_length(cls: Type[Hash128]) -> int:
        return 16
