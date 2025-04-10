"""Model for TrustSet transaction type."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.trust_set_flag import TrustSetFlag
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class TrustSet(Transaction):
    """
    Create or modify a trust line linking two accounts.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.TRUST_SET,
        init=False
    )

    limit_amount: Optional[Any] = REQUIRED
    """
    Object defining the trust line to create or modify, in the format of a Currency Amount.
    """

    quality_in: Optional[int] = None
    """
    (Optional) Value incoming balances on this trust line at the ratio of this number per
    1,000,000,000 units. A value of 0 is shorthand for treating balances at face value.
    """

    quality_out: Optional[int] = None
    """
    (Optional) Value outgoing balances on this trust line at the ratio of this number per
    1,000,000,000 units. A value of 0 is shorthand for treating balances at face value.
    """

class TrustSetFlagInterface(FlagInterface):
    """
    Enum for TrustSet Transaction Flags.
    """

    TF_SETF_AUTH: bool
    TF_SET_NO_RIPPLE: bool
    TF_CLEAR_NO_RIPPLE: bool
    TF_SET_FREEZE: bool
    TF_CLEAR_FREEZE: bool

class TrustSetFlag(int, Enum):
    """
    Enum for TrustSet Transaction Flags.
    """

    TF_SETF_AUTH = 0x00010000
    """
    Authorize the other party to hold currency issued by this account. (No effect unless using the asfRequireAuth AccountSet flag.) Cannot be unset.
    """

    TF_SET_NO_RIPPLE = 0x00020000
    """
    Enable the No Ripple flag, which blocks rippling between two trust lines of the same currency if this flag is enabled on both.
    """

    TF_CLEAR_NO_RIPPLE = 0x00040000
    """
    Disable the No Ripple flag, allowing rippling on this trust line.
    """

    TF_SET_FREEZE = 0x00100000
    """
    Freeze the trust line.
    """

    TF_CLEAR_FREEZE = 0x00200000
    """
    Unfreeze the trust line.
    """


