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

    tf_set_auth: Optional[bool] = None
    """
    Authorize the other party to hold
    `currency issued by this account <https://xrpl.org/tokens.html>`_.
    (No effect unless using the `asfRequireAuth AccountSet flag
    <https://xrpl.org/accountset.html#accountset-flags>`_.) Cannot be unset.
    """

    tf_set_no_ripple: Optional[bool] = None
    """
    Enable the No Ripple flag, which blocks
    `rippling <https://xrpl.org/rippling.html>`_ between two trust
    lines of the same currency if this flag is enabled on both.
    """

    tf_clear_no_ripple: Optional[bool] = None
    """Disable the No Ripple flag, allowing rippling on this trust line."""

    tf_set_freeze: Optional[bool] = None
    """Freeze the trust line."""

    tf_clear_freeze: Optional[bool] = None
    """Unfreeze the trust line."""

    transaction_type: TransactionType = field(
        default=TransactionType.TRUST_SET,
        init=False,
    )
