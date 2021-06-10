"""
Represents a TrustSet transaction on the XRP Ledger.
Creates or modifies a trust line linking two accounts.

`See TrustSet <https://xrpl.org/trustset.html>`_
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init


class TrustSetFlag(int, Enum):
    """
    Transactions of the TrustSet type support additional values in the Flags field.
    This enum represents those options.
    """

    TF_SET_AUTH = 0x00010000
    TF_SET_NO_RIPPLE = 0x00020000
    TF_CLEAR_NO_RIPPLE = 0x00040000
    TF_SET_FREEZE = 0x00100000
    TF_CLEAR_FREEZE = 0x00200000


@require_kwargs_on_init
@dataclass(frozen=True)
class TrustSet(Transaction):
    """
    Represents a TrustSet transaction on the XRP Ledger.
    Creates or modifies a trust line linking two accounts.

    `See TrustSet <https://xrpl.org/trustset.html>`_
    """

    limit_amount: IssuedCurrencyAmount = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """

    quality_in: Optional[int] = None
    quality_out: Optional[int] = None
    transaction_type: TransactionType = field(
        default=TransactionType.TRUST_SET,
        init=False,
    )
