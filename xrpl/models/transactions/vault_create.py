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
    KW_ONLY_DATACLASS,
    MAX_MPTOKEN_METADATA_LENGTH,
    MPT_META_WARNING_HEADER,
    require_kwargs_on_init,
    validate_mptoken_metadata,
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


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
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
    Arbitrary metadata about the share MPT, in hex format, limited to 1024 bytes.

    The decoded value must be a UTF-8 encoded JSON object that adheres to the
    XLS-89d MPTokenMetadata standard.

    While adherence to the XLS-89d format is not mandatory, non-compliant metadata
    may not be discoverable by ecosystem tools such as explorers and indexers.
    """

    domain_id: Optional[str] = None
    """The PermissionedDomain object ID associated with the shares of this Vault."""

    withdrawal_policy: Optional[Union[int, WithdrawalPolicy]] = None
    """Indicates the withdrawal strategy used by the Vault. The below withdrawal policy
    is supported:

    Strategy Name	                      Value	          Description
    vaultStrategyFirstComeFirstServe	   1	          Requests are processed on a first-
                                                            come-first-serve basis.
    """

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

        if self.mptoken_metadata is not None:
            validation_messages = validate_mptoken_metadata(self.mptoken_metadata)

            if len(validation_messages) > 0:
                message = "\n".join(
                    [MPT_META_WARNING_HEADER]
                    + [f"- {msg}" for msg in validation_messages]
                )
                warnings.warn(message, stacklevel=5)

        return errors
