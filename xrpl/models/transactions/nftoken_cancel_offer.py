"""Model for NFTokenCancelOffer transaction type."""

from dataclasses import dataclass, field

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class NFTokenCancelOffer(Transaction):
    """
    The NFTokenCancelOffer transaction creates an NFToken object and adds it to the
    relevant NFTokenPage object of the minter. If the transaction is
    successful, the newly minted token will be owned by the minter account
    specified by the transaction.
    """

    token_ids: str[] = REQUIRED
    """
    An array of TokenID objects, each identifying an
    NFTokenOffer object, which should be cancelled by this
    transaction.

    It is an error if an entry in this list points to an
    object that is not an NFTokenOffer object. It is not an
    error if an entry in this list points to an object that
    does not exist.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.NFTOKEN_CANCEL_OFFER,
        init=False,
    )