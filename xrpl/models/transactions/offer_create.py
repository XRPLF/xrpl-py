"""Model for OfferCreate transaction type."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional

from typing_extensions import Self

from xrpl.models.amounts import Amount
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction, TransactionFlagInterface
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import (
    KW_ONLY_DATACLASS,
    require_kwargs_on_init,
    validate_domain_id,
)


class OfferCreateFlag(int, Enum):
    """
    Transactions of the OfferCreate type support additional values in the Flags field.
    This enum represents those options.

    `See OfferCreate Flags <https://xrpl.org/offercreate.html#offercreate-flags>`_
    """

    TF_PASSIVE = 0x00010000
    """
    If enabled, the offer does not consume offers that exactly match it, and instead
    becomes an Offer object in the ledger. It still consumes offers that cross it.
    """

    TF_IMMEDIATE_OR_CANCEL = 0x00020000
    """
    Treat the offer as an `Immediate or Cancel order
    <https://en.wikipedia.org/wiki/Immediate_or_cancel>`_. If enabled, the offer
    never becomes a ledger object: it only tries to match existing offers in the
    ledger. If the offer cannot match any offers immediately, it executes
    "successfully" without trading any currency. In this case, the transaction has
    the result code `tesSUCCESS`, but creates no Offer objects in the ledger.
    """

    TF_FILL_OR_KILL = 0x00040000
    """
    Treat the offer as a `Fill or Kill order
    <https://en.wikipedia.org/wiki/Fill_or_kill>`_. Only try to match existing
    offers in the ledger, and only do so if the entire `TakerPays` quantity can be
    obtained. If the `fix1578 amendment
    <https://xrpl.org/known-amendments.html#fix1578>`_ is enabled and the offer
    cannot be executed when placed, the transaction has the result code `tecKILLED`;
    otherwise, the transaction uses the result code `tesSUCCESS` even when it was
    killed without trading any currency.
    """

    TF_SELL = 0x00080000
    """
    Exchange the entire `TakerGets` amount, even if it means obtaining more than the
    `TakerPays amount` in exchange.
    """

    TF_HYBRID = 0x00100000
    """
    Indicates the offer is hybrid. This flag cannot be set if the offer doesn't have a
    `DomainID`.
    """


class OfferCreateFlagInterface(TransactionFlagInterface):
    """
    Transactions of the OfferCreate type support additional values in the Flags field.
    This TypedDict represents those options.

    `See OfferCreate Flags <https://xrpl.org/offercreate.html#offercreate-flags>`_
    """

    TF_PASSIVE: bool
    TF_IMMEDIATE_OR_CANCEL: bool
    TF_FILL_OR_KILL: bool
    TF_SELL: bool
    TF_HYBRID: bool


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class OfferCreate(Transaction):
    """
    Represents an `OfferCreate <https://xrpl.org/offercreate.html>`_ transaction,
    which executes a limit order in the `decentralized exchange
    <https://xrpl.org/decentralized-exchange.html>`_. If the specified exchange
    cannot be completely fulfilled, it creates an Offer object for the remainder.
    Offers can be partially fulfilled.
    """

    taker_gets: Amount = REQUIRED  # type: ignore
    """
    The amount and type of currency being provided by the sender of this
    transaction. This field is required.

    :meta hide-value:
    """

    taker_pays: Amount = REQUIRED  # type: ignore
    """
    The amount and type of currency the sender of this transaction wants in
    exchange for the full ``taker_gets`` amount. This field is required.

    :meta hide-value:
    """

    expiration: Optional[int] = None
    """
    Time after which the offer is no longer active, in seconds since the
    Ripple Epoch.
    """

    offer_sequence: Optional[int] = None
    """
    The Sequence number (or Ticket number) of a previous OfferCreate to cancel
    when placing this Offer.
    """

    domain_id: Optional[str] = None
    """
    The domain that the offer must be a part of.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.OFFER_CREATE,
        init=False,
    )

    def _get_errors(self: Self) -> Dict[str, str]:
        errors = super()._get_errors()
        # Check for hybrid flag set without domain_id
        if self.has_flag(OfferCreateFlag.TF_HYBRID) and self.domain_id is None:
            errors["domain_id"] = (
                "Hybrid offer (tfHybrid flag) requires domain_id to be set."
            )
        if self.domain_id is not None:
            err = validate_domain_id(self.domain_id)
            if err:
                errors["domain_id"] = err
        return errors
