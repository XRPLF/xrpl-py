"""TODO: write docstring"""

from __future__ import annotations

from typing import Union

from xrpl.binary_codec.binary_wrappers.binary_parser import BinaryParser
from xrpl.binary_codec.exceptions import XRPLBinaryCodecException
from xrpl.binary_codec.types.serialized_type import SerializedType


class Blob(SerializedType):
    """TODO: write docstring"""

    def __init__(self, buffer: bytes):
        """TODO: write docstring"""
        super().__init__(buffer)

    @classmethod
    def from_parser(cls, parser: BinaryParser, hint: int):
        """TODO: write docstring"""
        pass

    @classmethod
    def from_value(cls, value: Union[Blob, str]):
        """TODO: write docstring"""
        if isinstance(value, str):
            return cls(bytes.fromhex(value))

        if isinstance(value, Blob):
            return value

        raise XRPLBinaryCodecException("Cannot construct Blob from value given")
