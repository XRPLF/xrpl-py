"""Model for NFTokenCreateOffer transaction type and related flag."""

from dataclasses import dataclass, field

from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init


class NFTokenCreateOfferFlag(int, Enum):
    """
    Transaction Flags for an NFTokenCreateOffer Transaction.
    """

    TF_SELL_TOKEN = 0x00000001
    """
    If set, indicates that the offer is a sell offer.
    Otherwise, it is a buy offer.
    """

@require_kwargs_on_init
@dataclass(frozen=True)
class NFTokenCreateOffer(Transaction):
    """
    The NFTokenCreateOffer transaction creates an NFToken object and adds it to the
    relevant NFTokenPage object of the minter. If the transaction is
    successful, the newly minted token will be owned by the minter account
    specified by the transaction.
    """

    account: str = REQUIRED
    """
    Indicates the AccountID of the account that initiated the
    transaction.
    """

    token_id: str = REQUIRED
    """
    Identifies the TokenID of the NFToken object that the
    offer references.
    """

    amount: Amount = REQUIRED
    """
    Indicates the amount expected or offered for the Token.

    The amount must be non-zero, except where this is an
    offer is an offer to sell and the asset is XRP; then it
    is legal to specify an amount of zero, which means that
    the current owner of the token is giving it away, gratis,
    either to anyone at all, or to the account identified by
    the Destination field.
    """

    owner: Optional[str] = None
    """
    Indicates the AccountID of the account that owns the
    corresponding NFToken.

    If the offer is to buy a token, this field must be present
    and it must be different than Account (since an offer to
    buy a token one already holds is meaningless).

    If the offer is to sell a token, this field must not be
    present, as the owner is, implicitly, the same as Account
    (since an offer to sell a token one doesn't already hold
    is meaningless).
    """

    expiration: Optional[int] = None
    """
    Indicates the time after which the offer will no longer
    be valid. The value is the number of seconds since the
    Ripple Epoch.
    """

    destination: Optional[str] = None
    """
    If present, indicates that this offer may only be
    accepted by the specified account. Attempts by other
    accounts to accept this offer MUST fail.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.NFTOKEN_CREATE_OFFER,
        init=False,
    )