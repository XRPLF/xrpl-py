"""Model for NFTokenAcceptOffer transaction type."""
from dataclasses import dataclass, field
from typing import Any, Optional
from xrpl.models.amounts import get_amount_value
from xrpl.models.transactions.types import TransactionType
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class NFTokenAcceptOffer(Transaction):
    """
    The NFTokenAcceptOffer transaction is used to accept offers to buy or sell an NFToken.
    It can either:  - Allow one offer to be accepted. This is called direct mode. - Allow
    two distinct offers, one offering to buy a given NFToken and the other offering to sell
    the same NFToken,    to be accepted in an atomic fashion. This is called brokered mode.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.NFTOKEN_ACCEPT_OFFER,
        init=False
    )

    nf_token_sell_offer: Optional[str] = None
    """
    (Optional) Identifies the NFTokenOffer that offers to sell the NFToken.
    """

    nf_token_buy_offer: Optional[str] = None
    """
    (Optional) Identifies the NFTokenOffer that offers to buy the NFToken.
    """

    nf_token_broker_fee: Optional[Any] = None
    """
    (Optional) This field is only valid in brokered mode, and specifies the amount that the
    broker keeps as part of their fee for bringing the two offers together; the remaining
    amount is sent to the seller of the NFToken being bought. If specified, the fee must be
    such that, before applying the transfer fee, the amount that the seller would receive is
    at least as much as the amount indicated in the sell offer.
    """

    def _get_errors(self: NFTokenAcceptOffer) -> Dict[str, str]:
        errors = super._get_errors()
        if (
            self.nftoken_broker_fee is not None and
            self.nftoken_buy_offer is None and 
            self.nftoken_sell_offer is None
        ):
            errors["NFTokenAcceptOffer"] = "Must set `nftoken_buy_offer`, `nftoken_sell_offer` with `nftoken_broker_fee.`"
        if (
            self.nftoken_sell_offer is None and
            self.nftoken_buy_offer is None
        ):
            errors["NFTokenAcceptOffer"] = "At least one of `nftoken_sell_offer`, `nftoken_buy_offer` must be set."
        if (
            self.nf_token_broker_fee is not None and 
            get_amount_value(self.nf_token_broker_fee) < 0
        ):
            return "`nf_token_broker_fee` value must be greater than 0"
        return errors


