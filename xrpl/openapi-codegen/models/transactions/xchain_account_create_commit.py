"""Model for XChainAccountCreateCommit transaction type."""

from dataclasses import dataclass, field
from typing import Optional
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.xchain_bridge import XChainBridge
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class XChainAccountCreateCommit(Transaction):
    """
    This transaction can only be used for XRP-XRP bridges.  The XChainAccountCreateCommit
    transaction creates a new account for a witness server to submit transactions on an
    issuing chain.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.XCHAIN_ACCOUNT_CREATE_COMMIT, init=False
    )

    amount: str = REQUIRED
    """
    The amount, in XRP, to use for account creation. This must be greater than or equal to
    the MinAccountCreateAmount specified in the Bridge ledger object.
    """

    destination: str = REQUIRED
    """
    The destination account on the destination chain.
    """

    signature_reward: Optional[str] = None
    """
    (Optional) The amount, in XRP, to be used to reward the witness servers for providing
    signatures. This must match the amount on the Bridge ledger object.
    """

    x_chain_bridge: XChainBridge = REQUIRED

    def _get_errors(self: XChainAccountCreateCommit) -> Dict[str, str]:
        errors = super._get_errors()
        if (
            self.amount is not None
            and self.amount != REQUIRED
            and not self.amount.isnumeric()
        ):
            errors["XChainAccountCreateCommit"] = "`amount` must be numeric."
        if (
            self.signature_reward is not None
            and self.signature_reward != REQUIRED
            and not self.signature_reward.isnumeric()
        ):
            errors["XChainAccountCreateCommit"] = "`signature_reward` must be numeric."
        return errors
