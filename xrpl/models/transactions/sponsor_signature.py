"""Model for the SponsorSignature inner object used in SponsorshipSet."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from xrpl.models.base_model import BaseModel
from xrpl.models.transactions.transaction import Signer
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init

# CK TODO: Add verification methods to validate the SponsorSignature values


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class SponsorSignature(BaseModel):
    """
    Signature payload supplied by the sponsor.
    Fields:
    - signing_pub_key: hex-encoded public key of the sponsor (required if
    txn_signature is set).
    - txn_signature: hex-encoded signature over the canonical transaction
    (required if signing_pub_key is set).
    - signers: optional multisign array reusing the standard Signer objects.
    """

    signing_pub_key: Optional[str] = None
    txn_signature: Optional[str] = None
    signers: Optional[List[Signer]] = None
