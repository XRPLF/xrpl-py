"""Model for NFTokenAcceptOffer transaction type."""

from dataclasses import dataclass, field
from typing import Optional

from xrpl.models.amounts import Amount
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class NFTokenAcceptOffer(Transaction):
    """
    The NFTokenAcceptOffer transaction creates an NFToken object and adds it to the
    relevant NFTokenPage object of the minter. If the transaction is
    successful, the newly minted token will be owned by the minter account
    specified by the transaction.
    """

    sell_offer: Optional[str] = None
    """
    Identifies the NFTokenOffer that offers to sell the NFToken.

    In direct mode this field is optional, but either SellOffer or
    BuyOffer must be specified. In brokered mode, both SellOffer
    and BuyOffer MUST be specified.
    """

    buy_offer: Optional[str] = None
    """
    Identifies the NFTokenOffer that offers to sell the NFToken.

    In direct mode this field is optional, but either SellOffer or
    BuyOffer must be specified. In brokered mode, both SellOffer
    and BuyOffer MUST be specified.
    """

    broker_fee: Optional[Amount] = None
    """
    This field is only valid in brokered mode and specifies the
    amount that the broker will keep as part of their fee for
    bringing the two offers together; the remaining amount will
    be sent to the seller of the NFToken being bought. If
    specified, the fee must be such that, prior to accounting
    for the transfer fee charged by the issuer, the amount that
    the seller would receive is at least as much as the amount
    indicated in the sell offer.

    This functionality is intended to allow the owner of an
    NFToken to offer their token for sale to a third party
    broker, who may then attempt to sell the NFToken on for a
    larger amount, without the broker having to own the NFToken
    or custody funds.

    If both offers are for the same asset, it is possible that
    the order in which funds are transferred might cause a
    transaction that would succeed to fail due to an apparent
    lack of funds. To ensure deterministic transaction execution
    and maximimize the chances of successful execution, this
    proposal requires that the account attempting to buy the
    NFToken is debited first and that funds due to the broker
    are credited before crediting the seller.

    Note: in brokered mode, The offers referenced by BuyOffer
    and SellOffer must both specify the same TokenID; that is,
    both must be for the same NFToken.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.NFTOKEN_ACCEPT_OFFER,
        init=False,
    )
