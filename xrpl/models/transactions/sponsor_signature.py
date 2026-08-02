"""Model for the SponsorSignature transaction common field."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from typing_extensions import Self

from xrpl.models.base_model import BaseModel
from xrpl.models.transactions.transaction import Signer


@dataclass(frozen=True, kw_only=True)
class SponsorSignature(BaseModel):
    """
    The sponsor's signing information for a fee-/reserve-sponsored transaction.

    Fields:
    - signing_pub_key: hex-encoded public key of the sponsor (required if
    txn_signature is set).
    - txn_signature: hex-encoded signature over the canonical transaction
    (required if signing_pub_key is set).
    - signers: optional multisign array reusing the standard Signer objects.

    All three fields are optional, and an **empty** ``SponsorSignature()`` is a
    valid, meaningful value in two cases:

    - **Batch inner transactions**. An inner transaction that
      names a ``sponsor`` must carry an empty placeholder; its *presence* --
      not its contents -- is what tells the ledger that the named sponsor needs
      an entry in the outer transaction's ``BatchSigners``. Populating any of
      the three fields on an inner transaction is rejected.
    - **``simulate``**. The server autofills the sponsor's
      signing fields only when the field is present, so a dry run of a
      sponsored transaction supplies the empty object.

    For an ordinary submitted transaction, populate either
    ``signing_pub_key`` + ``txn_signature`` (single-sign) or ``signers``
    (multi-sign) -- see :func:`xrpl.transaction.sign_as_sponsor`.
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
