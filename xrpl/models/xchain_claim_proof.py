"""
A XChainClaimProof represents a proof that a cross-chain transfer was initiated on the
source chain.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from xrpl.models.base_model import BaseModel
from xrpl.models.required import REQUIRED
from xrpl.models.sidechain import Sidechain
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class XChainProofSig(BaseModel):
    """
    A XChainClaimProof represents a proof that a cross-chain transfer was initiated on
    the source chain.
    """

    signature: str = REQUIRED  # type: ignore

    signing_key: str = REQUIRED  # type: ignore


@require_kwargs_on_init
@dataclass(frozen=True)
class XChainClaimProof(BaseModel):
    """A XChainClaimProof represents an individual step along a Path."""

    amount: str
    sidechain: Sidechain
    signatures: List[XChainProofSig]
    was_src_chain_send: bool
    xchain_seq: int
