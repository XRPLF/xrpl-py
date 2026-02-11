"""Model for SponsorSignature nested object used in sponsored transactions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from typing_extensions import Self

from xrpl.models.nested_model import NestedModel
from xrpl.models.required import REQUIRED
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class SponsorSigner(NestedModel):
    """
    One Signer in a multi-signature for a sponsor. A multi-signed sponsor can have an
    array of up to 8 SponsorSigners, each contributing a signature, in the Signers
    field of the SponsorSignature object.
    """

    account: str = REQUIRED
    """
    The address of the Signer. This can be a funded account in the XRP
    Ledger or an unfunded address.
    This field is required.

    :meta hide-value:
    """

    txn_signature: str = REQUIRED
    """
    The signature that this Signer provided for this transaction.
    This field is required.

    :meta hide-value:
    """

    signing_pub_key: str = REQUIRED
    """
    The public key that should be used to verify this Signer's signature.
    This field is required.

    :meta hide-value:
    """


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class SponsorSignature(NestedModel):
    """
    Represents the signature data from a sponsor in a sponsored transaction.
    This object contains the sponsor's signature information, which can be either
    a single signature or multi-signature data.

    For single-signed sponsors, use signing_pub_key and txn_signature.
    For multi-signed sponsors, use signers array and set signing_pub_key to empty string.
    """

    signing_pub_key: str = REQUIRED
    """
    The public key authorizing the sponsor's signature. For multi-signed sponsors,
    this should be an empty string.
    This field is required.

    :meta hide-value:
    """

    txn_signature: Optional[str] = None
    """
    The signature from the sponsor. Required for single-signed sponsors.
    Omitted for multi-signed sponsors.
    """

    signers: Optional[List[SponsorSigner]] = None
    """
    Array of SponsorSigner objects for multi-signed sponsors. Each SponsorSigner
    contributes a signature. Maximum of 8 signers.
    """

    def _get_errors(self: Self) -> Dict[str, str]:
        errors = super()._get_errors()

        # Check that either txn_signature or signers is provided, but not both
        has_single_sig = self.txn_signature is not None
        has_multi_sig = self.signers is not None and len(self.signers) > 0

        if not has_single_sig and not has_multi_sig:
            errors["SponsorSignature"] = (
                "SponsorSignature must contain either txn_signature "
                "(for single-signed) or signers (for multi-signed)"
            )

        if has_single_sig and has_multi_sig:
            errors["SponsorSignature"] = (
                "SponsorSignature cannot contain both txn_signature and signers"
            )

        # For multi-sig, signing_pub_key should be empty string
        if has_multi_sig and self.signing_pub_key != "":
            errors["signing_pub_key"] = (
                "signing_pub_key must be empty string for multi-signed sponsors"
            )

        # For single-sig, signing_pub_key should not be empty
        if has_single_sig and self.signing_pub_key == "":
            errors["signing_pub_key"] = (
                "signing_pub_key is required for single-signed sponsors"
            )

        # Check max signers limit
        if has_multi_sig and len(self.signers) > 8:  # type: ignore
            errors["signers"] = "Maximum of 8 signers allowed in SponsorSignature"

        return errors

