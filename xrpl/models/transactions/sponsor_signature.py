"""Model for the SponsorSignature inner object used in SponsorshipSet."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from typing_extensions import Self

from xrpl.models.base_model import BaseModel
from xrpl.models.transactions.transaction import Signer
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init


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

    def _get_errors(self: Self) -> Dict[str, str]:
        errors = super()._get_errors()

        has_single_sig = (
            self.signing_pub_key is not None or self.txn_signature is not None
        )
        has_multi_sig = self.signers is not None

        if has_single_sig and has_multi_sig:
            errors["SponsorSignature"] = (
                "Cannot set both single-signature fields "
                "(`signing_pub_key`/`txn_signature`) and `signers`."
            )
        elif not has_single_sig and not has_multi_sig:
            errors["SponsorSignature"] = (
                "Must provide either (`signing_pub_key` + `txn_signature`) "
                "for single-signature or `signers` for multi-signature."
            )
        elif has_single_sig:
            if self.signing_pub_key is None:
                errors["signing_pub_key"] = (
                    "`signing_pub_key` is required when `txn_signature` is set."
                )
            if self.txn_signature is None:
                errors["txn_signature"] = (
                    "`txn_signature` is required when `signing_pub_key` is set."
                )

        return errors
