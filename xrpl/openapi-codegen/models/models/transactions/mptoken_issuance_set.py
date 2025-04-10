"""Model for MPTokenIssuanceSet transaction type."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import REQUIRED
from xrpl.models.mptoken_issuance_set_flag import MPTokenIssuanceSetFlag
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class MPTokenIssuanceSet(Transaction):
    """
    Use this transaction to update a mutable property for a Multi-purpose Token.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.MPTOKEN_ISSUANCE_SET,
        init=False
    )

    mp_token_issuance_id: str = REQUIRED
    """
    The MPTokenIssuance identifier.
    """

    holder: Optional[str] = None
    """
    (Optional) XRPL Address of an individual token holder balance to lock/unlock. If
    omitted, this transaction applies to all any accounts holding MPTs.
    """

    def _get_errors(self: MPTokenIssuanceSet) -> Dict[str, str]:
        errors = super._get_errors()
        if (
            self.has_flag(MPTokenIssuanceSetFlag.TF_MPT_LOCK) and
            self.has_flag(MPTokenIssuanceSetFlag.TF_MPT_UNLOCK)
        ):
            errors["MPTokenIssuanceSet"] = "flag conflict: only of these flags `TF_MPT_LOCK`, `TF_MPT_UNLOCK` can be set"
        return errors

class MPTokenIssuanceSetFlagInterface(FlagInterface):
    """
    Enum for MPTokenIssuanceSet Transaction Flags.
    """

    TF_MPT_LOCK: bool
    TF_MPT_UNLOCK: bool

class MPTokenIssuanceSetFlag(int, Enum):
    """
    Enum for MPTokenIssuanceSet Transaction Flags.
    """

    TF_MPT_LOCK = 0x00000001
    """
    If set, indicates that all MPT balances for this asset should be locked.
    """

    TF_MPT_UNLOCK = 0x00000002
    """
    If set, indicates that all MPT balances for this asset should be unlocked.
    """


