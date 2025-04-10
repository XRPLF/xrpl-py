"""Model for OfferCreate transaction type."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import REQUIRED
from xrpl.models.offer_create_flag import OfferCreateFlag
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class OfferCreate(Transaction):
    """
    An OfferCreate transaction places an Offer in the decentralized exchange.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.OFFER_CREATE,
        init=False
    )

    expiration: Optional[int] = None
    """
    (Optional) Time after which the Offer is no longer active, in seconds since the Ripple
    Epoch.
    """

    offer_sequence: Optional[int] = None
    """
    (Optional) An Offer to delete first, specified in the same way as OfferCancel.
    """

    taker_gets: Optional[Any] = REQUIRED
    """
    The amount and type of currency being sold.
    """

    taker_pays: Optional[Any] = REQUIRED
    """
    The amount and type of currency being bought.
    """

class OfferCreateFlagInterface(FlagInterface):
    """
    Enum for OfferCreate Transaction Flags.
    """

    TF_PASSIVE: bool
    TF_IMMEDIATE_OR_CANCEL: bool
    TF_FILL_OR_KILL: bool
    TF_SELL: bool

class OfferCreateFlag(int, Enum):
    """
    Enum for OfferCreate Transaction Flags.
    """

    TF_PASSIVE = 0x00010000
    """
    If enabled, the Offer does not consume Offers that exactly match it, and instead becomes an Offer object in the ledger. It still consumes Offers that cross it.
    """

    TF_IMMEDIATE_OR_CANCEL = 0x00020000
    """
    Treat the Offer as an Immediate or Cancel order. The Offer never creates an Offer object in the ledger: it only trades as much as it can by consuming existing Offers at the time the transaction is processed. If no Offers match, it executes &quot;successfully&quot; without trading anything. In this case, the transaction still uses the result code tesSUCCESS.
    """

    TF_FILL_OR_KILL = 0x00040000
    """
    Treat the offer as a Fill or Kill order. The Offer never creates an Offer object in the ledger, and is canceled if it cannot be fully filled at the time of execution. By default, this means that the owner must receive the full TakerPays amount; if the tfSell flag is enabled, the owner must be able to spend the entire TakerGets amount instead.
    """

    TF_SELL = 0x00080000
    """
    Exchange the entire TakerGets amount, even if it means obtaining more than the TakerPays amount in exchange.
    """


