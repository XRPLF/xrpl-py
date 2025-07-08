"""Represents a VaultDeposit transaction on the XRP Ledger."""

from dataclasses import dataclass, field

from xrpl.models.amounts import Amount
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class VaultDeposit(Transaction):
    """The VaultDeposit transaction adds Liqudity in exchange for vault shares."""

    vault_id: str = REQUIRED
    """The ID of the vault to which the assets are deposited."""

    amount: Amount = REQUIRED
    """Asset amount to deposit."""

    transaction_type: TransactionType = field(
        default=TransactionType.VAULT_DEPOSIT,
        init=False,
    )
