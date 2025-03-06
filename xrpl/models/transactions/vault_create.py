"""
Represents a VaultCreate transaction on the XRP Ledger.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Union

from xrpl.models.amounts.mpt_amount import MPTIssue
from xrpl.models.currencies import Currency
from xrpl.models.flags import FlagInterface
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init


class VaultCreateFlag(int, Enum):

    TF_VAULT_PRIVATE = 0x0001
    TF_VAULT_SHARE_NON_TRANSFERABLE = 0x0002


class VaultCreateFlagInterface(FlagInterface):

    TF_VAULT_PRIVATE: bool
    TF_VAULT_SHARE_NON_TRANSFERABLE: bool


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class VaultCreate(Transaction):
    """
    The VaultCreate transaction creates a new Vault object.
    """

    data: Optional[str] = None
    """Arbitrary Vault metadata, limited to 256 bytes."""

    asset: Union[Currency, MPTIssue] = REQUIRED  # type: ignore
    """The asset (XRP, IOU or MPT) of the Vault."""

    asset_maximum: Optional[str] = None
    """The maximum asset amount that can be held in a vault."""

    mptoken_metadata: Optional[str] = None
    """Arbitrary metadata about the share MPT, in hex format, limited to 1024 bytes."""

    domain_id: Optional[str] = None
    """The PermissionedDomain object ID associated with the shares of this Vault."""

    withdrawal_policy: Optional[int] = None
    """Indicates the withdrawal strategy used by the Vault.
    
    The below withdrawal policy is supported:

    Strategy Name	           Value	      Description
    strFirstComeFirstServe	   1	          Requests are processed on a first-come-first-
                                                serve basis.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.VAULT_CREATE,
        init=False,
    )
