"""Model for NFTokenBurn transaction type."""

from dataclasses import dataclass, field

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class NFTokenBurn(Transaction):
    """
    The NFTokenBurn transaction is used to remove an NFToken object from the
    NFTokenPage in which it is being held, effectively removing the token from
    the ledger ("burning" it).

    If this operation succeeds, the corresponding NFToken is removed. If this
    operation empties the NFTokenPage holding the NFToken or results in the
    consolidation, thus removing an NFTokenPage, the owner’s reserve requirement
    is reduced by one.
    """

    account: str = REQUIRED  # type: ignore
    """
    Indicates the AccountID that submitted this transaction. The account MUST
    be either the present owner of the token or, if the lsfBurnable flag is set
    in the NFToken, either the issuer account or an account authorized by the
    issuer, i.e. MintAccount.
    """

    token_id: str = REQUIRED  # type: ignore
    """
    Identifies the NFToken object to be removed by the transaction.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.NFTOKEN_BURN,
        init=False,
    )
