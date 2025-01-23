"""
Represents a VaultDeposit transaction on the XRP Ledger.
"""

from dataclasses import dataclass, field
from typing import Union

from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class VaultDeposit(Transaction):
    """
    Represents a VaultDeposit transaction on the XRP Ledger.
    """

    vault_id: str = REQUIRED  # type: ignore
    amount: Union[str, IssuedCurrencyAmount] = REQUIRED  # type: ignore

    transaction_type: TransactionType = field(
        default=TransactionType.VAULT_DEPOSIT,
        init=False,
    )
