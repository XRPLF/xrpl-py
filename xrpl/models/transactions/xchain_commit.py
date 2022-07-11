"""Model for a XChainCommit transaction type."""

from dataclasses import dataclass, field
from typing import Union

from xrpl.models.amounts import Amount
from xrpl.models.bridge import Bridge
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class XChainCommit(Transaction):
    """Represents a XChainCommit transaction."""

    bridge: Bridge = REQUIRED  # type: ignore

    xchain_claim_id: Union[int, str] = REQUIRED  # type: ignore

    amount: Amount = REQUIRED  # type: ignore

    transaction_type: TransactionType = field(
        default=TransactionType.XCHAIN_CREATE_CLAIM_ID,
        init=False,
    )
