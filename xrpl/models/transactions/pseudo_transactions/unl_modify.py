"""Model for EnableAmendment pseudo-transaction type."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.pseudo_transactions.pseudo_transaction import (
    PseudoTransaction,
)
from xrpl.models.transactions.types import PseudoTransactionType
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class UNLModify(PseudoTransaction):
    """
    An UNLModify pseudo-transaction marks a change in status of an amendment to
    the XRP Ledger protocol, including:

    * A proposed amendment gained supermajority approval from validators.
    * A proposed amendment lost supermajority approval.
    * A proposed amendment has been enabled.
    """

    #: The ledger index where this pseudo-transaction appears. This distinguishes the
    #: pseudo-transaction from other occurrences of the same change.
    #: This field is required.
    ledger_sequence: str = REQUIRED  # type: ignore

    #: If 1, this change represents adding a validator to the Negative UNL. If 0, this
    #: change represents removing a validator from the Negative UNL. (No other values
    #: are allowed.)
    unl_modify_disabling: int = REQUIRED  # type: ignore

    #: The validator to add or remove, as identified by its master public key.
    unl_modify_validator: str = REQUIRED  # type: ignore

    transaction_type: PseudoTransactionType = field(
        default=PseudoTransactionType.UNL_MODIFY,
        init=False,
    )

    #: The Flags value of the EnableAmendment pseudo-transaction indicates the status
    #: of the amendment at the time of the ledger including the pseudo-transaction.
    #: A Flags value of 0 (no flags) or an omitted Flags field indicates that the
    #: amendment has been enabled, and applies to all ledgers afterward.
    flags: int = 0

    def _get_errors(self: UNLModify) -> Dict[str, str]:
        errors = super()._get_errors()
        if self.unl_modify_disabling not in {0, 1}:
            errors[
                "unl_modify_disabling"
            ] = "`unl_modify_disabling` is not equal to 0 or 1."

        return errors
