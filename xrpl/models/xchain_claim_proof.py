"""
A path is an ordered array. Each member of a path is an
object that specifies the step.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Type, cast

from xrpl.models.base_model import BaseModel
from xrpl.models.required import REQUIRED
from xrpl.models.sidechain import Sidechain
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class XChainProofSig(BaseModel):

    signature: str = REQUIRED  # type: ignore

    public_key: str = REQUIRED  # type: ignore

    @classmethod
    def is_dict_of_model(cls: Type[XChainProofSig], dictionary: Any) -> bool:
        return (
            isinstance(dictionary, dict)
            and "xchain_proof_sig" in dictionary
            and super().is_dict_of_model(dictionary["xchain_proof_sig"])
        )

    @classmethod
    def from_dict(cls: Type[XChainProofSig], value: Dict[str, Any]) -> XChainProofSig:
        if "xchain_proof_sig" not in value:
            return cast(XChainProofSig, super(XChainProofSig, cls).from_dict(value))
        return cast(
            XChainProofSig,
            super(XChainProofSig, cls).from_dict(value["xchain_proof_sig"]),
        )

    def to_dict(self: XChainProofSig) -> Dict[str, Any]:
        return {"xchain_proof_sig": super().to_dict()}


@require_kwargs_on_init
@dataclass(frozen=True)
class XChainClaimProof(BaseModel):
    """A XChainClaimProof represents an individual step along a Path."""

    amount: str
    sidechain: Sidechain
    signatures: List[XChainProofSig]
    was_src_chain_send: bool
    xchain_seq: int
