"""
A XChainClaimProof represents a proof that a cross-chain transfer was initiated on the
source chain.
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
    """
    A XChainClaimProof represents a proof that a cross-chain transfer was initiated on
    the source chain.
    """

    signature: str = REQUIRED  # type: ignore

    signing_key: str = REQUIRED  # type: ignore

    @classmethod
    def is_dict_of_model(cls: Type[XChainProofSig], dictionary: Any) -> bool:
        """
        Returns True if the input dictionary was derived by the `to_dict`
        method of an instance of this class. In other words, True if this is
        a dictionary representation of an instance of this class.

        NOTE: does not account for model inheritance, IE will only return True
        if dictionary represents an instance of this class, but not if
        dictionary represents an instance of a subclass of this class.

        Args:
            dictionary: The dictionary to check.

        Returns:
            True if dictionary is a dict representation of an instance of this
            class.
        """
        return (
            isinstance(dictionary, dict)
            and "xchain_proof_sig" in dictionary
            and super().is_dict_of_model(dictionary["xchain_proof_sig"])
        )

    @classmethod
    def from_dict(cls: Type[XChainProofSig], value: Dict[str, Any]) -> XChainProofSig:
        """
        Construct a new XChainProofSig from a dictionary of parameters.

        Args:
            value: The value to construct the XChainProofSig from.

        Returns:
            A new XChainProofSig object, constructed using the given parameters.

        Raises:
            XRPLModelException: If the dictionary provided is invalid.
        """
        if "xchain_proof_sig" not in value:
            return cast(XChainProofSig, super(XChainProofSig, cls).from_dict(value))
        return cast(
            XChainProofSig,
            super(XChainProofSig, cls).from_dict(value["xchain_proof_sig"]),
        )

    def to_dict(self: XChainProofSig) -> Dict[str, Any]:
        """
        Returns the dictionary representation of a XChainProofSig.

        Returns:
            The dictionary representation of a XChainProofSig.
        """
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
