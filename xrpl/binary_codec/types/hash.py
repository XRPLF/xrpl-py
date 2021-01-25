"""Base class for XRPL Hash types.
`See Hash Fields <https://xrpl.org/serialization.html#hash-fields>`_
"""
from abc import ABC

from xrpl.binary_codec.exceptions import XRPLBinaryCodecException
from xrpl.binary_codec.types.serialized_type import SerializedType


class Hash(SerializedType, ABC):
    """
    Base class for XRPL Hash types.
    `See Hash Fields <https://xrpl.org/serialization.html#hash-fields>`_

    Attributes:
        width:  The length of this hash in bytes.
    """

    _width: int

    def __init__(self, buffer: bytes):
        """
        Construct a Hash.

        :param buffer: The byte buffer that will be used to store
                        the serialized encoding of this field.
        """
        if len(buffer) != self._width:
            raise XRPLBinaryCodecException("Invalid hash length {}".format(len(buffer)))
        super().__init__(buffer)

    def __str__(self):
        """Returns a hex-encoded string representation of the bytes buffer."""
        return self.to_hex()
