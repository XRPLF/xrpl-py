"""Represents a VaultClawback transaction on the XRP Ledger."""

from dataclasses import dataclass, field
from typing import Optional

from xrpl.models.amounts import ClawbackAmount
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class VaultClawback(Transaction):
    """
    The VaultClawback transaction performs a Clawback from the Vault, exchanging the
    shares of an account. Conceptually, the transaction performs VaultWithdraw on
    behalf of the Holder, sending the funds to the Issuer account of the asset.

    In case there are insufficient funds for the entire Amount the transaction will
    perform a partial Clawback, up to the Vault.AssetAvailable.

    The Clawback transaction must respect any future fees or penalties.
    """

    vault_id: str = REQUIRED
    """The ID of the vault from which assets are withdrawn."""

    holder: str = REQUIRED
    """The account ID from which to clawback the assets."""

    amount: Optional[ClawbackAmount] = None
    """The asset amount to clawback. When Amount is 0 clawback all funds, up to the
    total shares the Holder owns.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.VAULT_CLAWBACK,
        init=False,
    )
