"""Model for TicketCreate transaction type."""
from dataclasses import dataclass, field
from typing import Optional
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class TicketCreate(Transaction):
    """
    A TicketCreate transaction sets aside one or more sequence numbers as Tickets.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.TICKET_CREATE,
        init=False
    )

    ticket_count: int = REQUIRED
    """
    How many Tickets to create. This must be a positive number and cannot cause the account
    to own more than 250 Tickets after executing this transaction.
    """

    def _get_errors(self: TicketCreate) -> Dict[str, str]:
        errors = super._get_errors()
        if self.ticket_count is not None and self.ticket_count < 1:
            errors["TicketCreate"] = "Field `ticket_count` must have a value greater than or equal to 1"
        if self.ticket_count is not None and self.ticket_count > 250:
            errors["TicketCreate"] = "Field `ticket_count` must have a value less than or equal to 250"
        return errors


