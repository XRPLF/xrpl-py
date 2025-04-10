"""Model for Clawback transaction type."""
from dataclasses import dataclass, field
from typing import Optional
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import REQUIRED
from xrpl.models.token_amount import TokenAmount
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class Clawback(Transaction):
    """
    Claw back tokens issued by your account.  Clawback is disabled by default. To use
    clawback, you must send an AccountSet transaction to enable the Allow Trust Line
    Clawback setting. An issuer with any existing tokens cannot enable Clawback. You can
    only enable Allow Trust Line Clawback if you have a completely empty owner directory,
    meaning you must do so before you set up any trust lines, offers, escrows, payment
    channels, checks, or signer lists. After you enable Clawback, it cannot be reverted: the
    account permanently gains the ability to claw back issued assets on trust lines.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.CLAWBACK,
        init=False
    )

    amount: TokenAmount = REQUIRED
    """
    Indicates the amount being clawed back, as well as the counterparty from which the
    amount is being clawed back. The quantity to claw back, in the value sub-field, must not
    be zero. If this is more than the current balance, the transaction claws back the entire
    balance. The sub-field issuer within Amount represents the token holder's account ID,
    rather than the issuer's.
    """

    holder: Optional[str] = None
    """
    (Optional) Specifies the holder's address from which to claw back. The holder must
    already own an MPToken object with a non-zero balance. (Requires the MPToken amendment.)
    """

    def _get_errors(self: Clawback) -> Dict[str, str]:
        errors = super._get_errors()
        if self.account is not None and self.account == self.amount.issuer:
            errors[Clawback] = "account must not be equal to amount.issuer."
        return errors


