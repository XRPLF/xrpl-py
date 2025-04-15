"""Model for AMMDelete transaction type."""

from dataclasses import dataclass, field
from typing import Optional
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import REQUIRED
from xrpl.models.currency import Currency
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class AMMDelete(Transaction):
    """
    Delete an empty Automated Market Maker (AMM) instance that could not be fully deleted
    automatically.  Normally, an AMMWithdraw transaction automatically deletes an AMM and
    all associated ledger entries when it withdraws all the assets from the AMM's pool.
    However, if there are too many trust lines to the AMM account to remove in one
    transaction, it may stop before fully removing the AMM. Similarly, an AMMDelete
    transaction removes up to a maximum of 512 trust lines; it may take several AMMDelete
    transactions to delete all the trust lines and the associated AMM. In all cases, only
    the last such transaction deletes the AMM and AccountRoot ledger entries.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.AMM_DELETE, init=False
    )

    asset: Currency = REQUIRED
    """
    (Required) The definition for one of the assets in the AMM's pool. In JSON, this is an
    object with currency and issuer fields (omit issuer for XRP).
    """

    asset2: Currency = REQUIRED
    """
    (Required) The definition for the other asset in the AMM's pool. In JSON, this is an
    object with currency and issuer fields (omit issuer for XRP).
    """
