"""Base class for XRPL Hash types.
`See Hash Fields <https://xrpl.org/serialization.html#hash-fields>`_
"""
from __future__ import annotations  # Requires Python 3.7+

from abc import ABC
from typing import Optional, Type

from xrpl.binarycodec.exceptions import XRPLBinaryCodecException
from xrpl.binarycodec.types.serialized_type import SerializedType


class Hash(SerializedType, ABC):
    """
    Base class for XRPL Hash types.
    `See Hash Fields <https://xrpl.org/serialization.html#hash-fields>`_
    """

    def __init__(self: Hash, buffer: Optional[bytes]) -> None:
        """
        Construct a Hash.

        Args:
            buffer: The byte buffer that will be used to store the serialized
                encoding of this field.
        """
        buffer = buffer if buffer is not None else bytes(self._get_length())

        if len(buffer) != self._get_length():
            raise XRPLBinaryCodecException("Invalid hash length {}".format(len(buffer)))
        super().__init__(buffer)

    def __str__(self: Hash) -> str:
        """Returns a hex-encoded string representation of the bytes buffer."""
        return self.to_hex()

    @classmethod
    def _get_length(cls: Type[Hash]) -> int:
        raise NotImplementedError("Hash._get_length not implemented")
