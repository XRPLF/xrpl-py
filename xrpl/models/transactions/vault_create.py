"""Represents a VaultCreate transaction on the XRP Ledger."""

import warnings
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, Union

from typing_extensions import Self

from xrpl.models.currencies import Currency
from xrpl.models.flags import FlagInterface
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import (
    HEX_REGEX,
    MAX_MPTOKEN_METADATA_LENGTH,
    MPT_META_WARNING_HEADER,
)

VAULT_MAX_DATA_LENGTH = 256 * 2
VAULT_MAX_DOMAIN_ID_LENGTH = 32 * 2


class VaultCreateFlag(int, Enum):
    """Flags for the VaultCreate transaction."""

    TF_VAULT_PRIVATE = 0x00010000
    """
    Indicates that the vault is private. It can only be set during Vault creation.
    """
    TF_VAULT_SHARE_NON_TRANSFERABLE = 0x00020000
    """
    Indicates the vault share is non-transferable. It can only be set during Vault
    creation.
    """


class VaultCreateFlagInterface(FlagInterface):
    """Interface for the VaultCreate transaction flags."""

    TF_VAULT_PRIVATE: bool
    """
    Indicates that the vault is private. It can only be set during Vault creation.
    """
    TF_VAULT_SHARE_NON_TRANSFERABLE: bool
    """
    Indicates the vault share is non-transferable. It can only be set during Vault
    creation.
    """


class WithdrawalPolicy(int, Enum):
    """Withdrawal policy for the Vault."""

    VAULT_STRATEGY_FIRST_COME_FIRST_SERVE = 1
    """Requests are processed on a first-come-first-serve basis."""


class VaultKind(int, Enum):
    """The kind of Vault (XLS-587, close-ended vaults)."""

    OPEN = 0
    """An open-ended vault: shares can be redeemed at any time."""
    CLOSED = 1
    """A close-ended vault: deposits and redemptions are restricted to the
    subscription and redemption periods respectively."""


@dataclass(frozen=True, kw_only=True)
class VaultCreate(Transaction):
    """The VaultCreate transaction creates a new Vault object."""

    asset: Currency = REQUIRED
    """The asset (XRP, IOU or MPT) of the Vault."""

    data: Optional[str] = None
    """Arbitrary Vault metadata, limited to 256 bytes."""

    assets_maximum: Optional[str] = None
    """The maximum asset amount that can be held in a vault."""

    mptoken_metadata: Optional[str] = None
    """
    Arbitrary metadata about this issuance, in hex format, limited to 1024 bytes.
    Use `encode_mptoken_metadata` to convert from a JSON object to this format.
    Use `decode_mptoken_metadata` to convert from this format to a JSON object.

    While adherence to the XLS-89d format is not mandatory, non-compliant metadata
    may not be discoverable by ecosystem tools such as explorers and indexers.
    """

    domain_id: Optional[str] = None
    """The PermissionedDomain object ID associated with the shares of this Vault."""

    scale: Optional[int] = None
    """(Trust line tokens only) Specifies decimal precision for share calculations.
    Assets are multiplied by 10^Scale to convert fractional amounts into whole number
    shares. For example, with a Scale of 6, depositing 20.3 units creates 20,300,000
    shares (20.3 × 10^Scale). For trust line tokens this can be configured at vault
    creation, and valid values are between 0-18, with the default being 6. For XRP and
    MPTs, this is fixed at 0."""

    withdrawal_policy: Optional[Union[int, WithdrawalPolicy]] = None
    """Indicates the withdrawal strategy used by the Vault. The below withdrawal policy
    is supported:

    Strategy Name	                      Value	          Description
    vaultStrategyFirstComeFirstServe	   1	          Requests are processed on a first-
                                                            come-first-serve basis.
    """

    vault_kind: Optional[Union[int, VaultKind]] = None
    """(XLS-587) The kind of Vault: 0 for an open-ended vault (the default) or 1 for a
    close-ended vault. Can only be set at Vault creation."""

    subscription_date: Optional[int] = None
    """(XLS-587, close-ended vaults only) The time, in seconds since the Ripple Epoch,
    up to which deposits into the Vault are accepted."""

    redemption_date: Optional[int] = None
    """(XLS-587, close-ended vaults only) The time, in seconds since the Ripple Epoch,
    at which shares may begin to be redeemed from the Vault."""

    transaction_type: TransactionType = field(
        default=TransactionType.VAULT_CREATE,
        init=False,
    )

    def _get_errors(self: Self) -> Dict[str, str]:
        errors = super()._get_errors()

        if self.data is not None and len(self.data) > VAULT_MAX_DATA_LENGTH:
            errors["data"] = (
                "Data must be less than 256 bytes (alternatively, 512 hex characters)."
            )
        if self.mptoken_metadata is not None and (
            len(self.mptoken_metadata) == 0
            or len(self.mptoken_metadata) > MAX_MPTOKEN_METADATA_LENGTH
            or not HEX_REGEX.fullmatch(self.mptoken_metadata)
        ):
            errors["mptoken_metadata"] = (
                "Metadata must be valid non-empty hex string less than 1024 bytes "
                "(alternatively, 2048 hex characters)."
            )
        if (
            self.domain_id is not None
            and len(self.domain_id) != VAULT_MAX_DOMAIN_ID_LENGTH
        ):
            errors["domain_id"] = (
                "Invalid domain ID: Length must be 32 characters (64 hex characters)."
            )

        if self.scale is not None:
            if self.scale > 18:
                errors["VaultCreate"] = (
                    "Scale field is higher than the allowed limit (18)"
                )
            elif self.scale < 0:
                errors["VaultCreate"] = (
                    "Scale field is lower than the allowed limit (0)"
                )

        # XLS-587 close-ended vault rules. A close-ended vault (VaultKind == 1)
        # requires both a subscription and a redemption date; an open-ended vault
        # (the default) must not carry either date.
        is_closed_ended = self.vault_kind == VaultKind.CLOSED
        has_subscription = self.subscription_date is not None
        has_redemption = self.redemption_date is not None
        if is_closed_ended:
            if not (has_subscription and has_redemption):
                errors["vault_kind"] = (
                    "A close-ended vault requires both subscription_date and "
                    "redemption_date."
                )
        elif has_subscription or has_redemption:
            errors["vault_kind"] = (
                "subscription_date and redemption_date can only be set on a "
                "close-ended vault (vault_kind=1)."
            )

        if self.mptoken_metadata is not None:
            # Lazy import to avoid circular dependency
            from xrpl.utils.mptoken_metadata import validate_mptoken_metadata

            validation_messages = validate_mptoken_metadata(self.mptoken_metadata)

            if len(validation_messages) > 0:
                message = "\n".join(
                    [MPT_META_WARNING_HEADER]
                    + [f"- {msg}" for msg in validation_messages]
                )
                warnings.warn(message, stacklevel=5)

        return errors
