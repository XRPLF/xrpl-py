"""Model for SetFee pseudo-transaction type."""

from dataclasses import dataclass, field
from typing import Optional

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.pseudo_transactions.pseudo_transaction import (
    PseudoTransaction,
)
from xrpl.models.transactions.types import PseudoTransactionType
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class SetFee(PseudoTransaction):
    """
    A SetFee pseudo-transaction marks a change in `transaction cost
    <https://xrpl.org/transaction-cost.html>`_ or `reserve requirements
    <https://xrpl.org/reserves.html>`_ as a result of `Fee Voting
    <https://xrpl.org/fee-voting.html>`_.
    """

    base_fee: str = REQUIRED  # type: ignore
    """
    The charge, in drops of XRP, for the reference transaction, as hex. (This is the
    transaction cost before scaling for load.) This field is required.

    :meta hide-value:
    """

    reference_fee_units: int = REQUIRED  # type: ignore
    """
    The cost, in fee units, of the reference transaction. This field is required.

    :meta hide-value:
    """

    reserve_base: int = REQUIRED  # type: ignore
    """
    The base reserve, in drops. This field is required.

    :meta hide-value:
    """

    reserve_increment: int = REQUIRED  # type: ignore
    """
    The incremental reserve, in drops. This field is required.

    :meta hide-value:
    """

    ledger_sequence: Optional[int] = None
    """
    The index of the ledger version where this pseudo-transaction appears. This
    distinguishes the pseudo-transaction from other occurrences of the same change.
    This field is omitted for some historical SetFee pseudo-transactions.
    """

    transaction_type: PseudoTransactionType = field(
        default=PseudoTransactionType.SET_FEE,
        init=False,
    )
