"""Codec for serializing and deserializing cross-chain claim proof fields."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, Type, Union

from xrpl.core.binarycodec.binary_wrappers.binary_parser import BinaryParser
from xrpl.core.binarycodec.exceptions import XRPLBinaryCodecException
from xrpl.core.binarycodec.types.amount import Amount
from xrpl.core.binarycodec.types.serialized_type import SerializedType
from xrpl.core.binarycodec.types.sidechain import Sidechain
from xrpl.core.binarycodec.types.st_array import STArray
from xrpl.core.binarycodec.types.uint8 import UInt8
from xrpl.core.binarycodec.types.uint32 import UInt32
from xrpl.models.xchain_claim_proof import XChainClaimProof as XChainClaimProofModel

_TYPE_ORDER: List[Tuple[str, Type[SerializedType]]] = [
    ("sidechain", Sidechain),
    ("amount", Amount),
    ("xchain_seq", UInt32),
    ("was_src_chain_send", UInt8),
    ("signatures", STArray),
]


class XChainClaimProof(SerializedType):
    """Codec for serializing and deserializing cross-chain claim proof fields."""

    def __init__(self: XChainClaimProof, buffer: bytes) -> None:
        """Construct an XChainClaimProof from given bytes."""
        super().__init__(buffer)

    @classmethod
    def from_value(
        cls: Type[XChainClaimProof], value: Union[str, Dict[str, str]]
    ) -> XChainClaimProof:
        """
        Construct a XChainClaimProof object from a dictionary representation of a
        cross-chain claim proof.

        Args:
            value: The dictionary to construct a XChainClaimProof object from.

        Returns:
            A XChainClaimProof object constructed from value.

        Raises:
            XRPLBinaryCodecException: If the XChainClaimProof representation is invalid.
        """
        if XChainClaimProofModel.is_dict_of_model(value):
            buffer = b""
            for (name, object_type) in _TYPE_ORDER:
                obj = object_type.from_value(value[name])
                buffer += bytes(obj)
            return cls(buffer)

        raise XRPLBinaryCodecException(
            "Invalid type to construct an XChainClaimProof: expected dict,"
            f" received {value.__class__.__name__}."
        )

    @classmethod
    def from_parser(
        cls: Type[XChainClaimProof],
        parser: BinaryParser,
        length_hint: Optional[int] = None,
    ) -> XChainClaimProof:
        """
        Construct a XChainClaimProof object from an existing BinaryParser.

        Args:
            parser: The parser to construct the XChainClaimProof object from.
            length_hint: The number of bytes to consume from the parser.

        Returns:
            The XChainClaimProof object constructed from a parser.
        """
        buffer = b""

        for (_, object_type) in _TYPE_ORDER:
            obj = object_type.from_parser(parser)
            buffer += bytes(obj)

        return cls(buffer)

    def to_json(self: XChainClaimProof) -> Union[str, Dict[Any, Any]]:
        """
        Returns the JSON representation of a cross-chain claim proof.

        Returns:
            The JSON representation of a XChainClaimProof.
        """
        parser = BinaryParser(str(self))
        return_json = {}
        for (name, object_type) in _TYPE_ORDER:
            obj = object_type.from_parser(parser)
            return_json[name] = obj.to_json()

        return return_json
