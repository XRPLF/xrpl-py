"""Represents a VaultCreate transaction on the XRP Ledger."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, Union

from typing_extensions import Self

from xrpl.models.amounts.mpt_amount import MPTIssue
from xrpl.models.currencies import Currency
from xrpl.models.flags import FlagInterface
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init


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


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class VaultCreate(Transaction):
    """The VaultCreate transaction creates a new Vault object."""

    asset: Union[Currency, MPTIssue] = REQUIRED  # type: ignore
    """The asset (XRP, IOU or MPT) of the Vault."""

    data: Optional[str] = None
    """Arbitrary Vault metadata, limited to 256 bytes."""

    assets_maximum: Optional[str] = None
    """The maximum asset amount that can be held in a vault."""

    mptoken_metadata: Optional[str] = None
    """Arbitrary metadata about the share MPT, in hex format, limited to 1024 bytes."""

    domain_id: Optional[str] = None
    """The PermissionedDomain object ID associated with the shares of this Vault."""

    withdrawal_policy: Optional[int] = None
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

        if self.data is not None and len(self.data) > 256:
            errors["data"] = "Data must be less than 256 bytes."
        if self.mptoken_metadata is not None and len(self.mptoken_metadata) > 1024:
            errors["mptoken_metadata"] = "Metadata must be less than 1024 bytes."
        if self.domain_id is not None and len(self.domain_id) != 32:
            errors["domain_id"] = "Invalid domain ID."

        return errors
