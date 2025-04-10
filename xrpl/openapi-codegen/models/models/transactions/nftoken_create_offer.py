"""Model for NFTokenCreateOffer transaction type."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import REQUIRED
from xrpl.models.nftoken_create_offer_flag import NFTokenCreateOfferFlag
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class NFTokenCreateOffer(Transaction):
    """
    Creates either a new Sell offer for an NFToken owned by the account executing the
    transaction, or a new Buy offer for an NFToken owned by another account.  If successful,
    the transaction creates an NFTokenOffer object. Each offer counts as one object towards
    the owner reserve of the account that placed the offer.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.NFTOKEN_CREATE_OFFER,
        init=False
    )

    owner: Optional[str] = None
    """
    (Optional) Who owns the corresponding NFToken. If the offer is to buy a token, this
    field must be present and it must be different than the Account field (since an offer to
    buy a token one already holds is meaningless). If the offer is to sell a token, this
    field must not be present, as the owner is, implicitly, the same as the Account (since
    an offer to sell a token one doesn't already hold is meaningless).
    """

    nf_token_id: str = REQUIRED
    """
    Identifies the NFToken object that the offer references.
    """

    amount: Optional[Any] = REQUIRED
    """
    Indicates the amount expected or offered for the corresponding NFToken. The amount must
    be non-zero, except where this is an offer to sell and the asset is XRP; then, it is
    legal to specify an amount of zero, which means that the current owner of the token is
    giving it away, gratis, either to anyone at all, or to the account identified by the
    Destination field.
    """

    expiration: Optional[int] = None
    """
    (Optional) Time after which the offer is no longer active, in seconds since the Ripple
    Epoch.
    """

    destination: Optional[str] = None
    """
    (Optional) If present, indicates that this offer may only be accepted by the specified
    account. Attempts by other accounts to accept this offer MUST fail.
    """

    def _get_errors(self: NFTokenCreateOffer) -> Dict[str, str]:
        errors = super._get_errors()
        if self.destination is not None and self.destination == self.account:
            errors[NFTokenCreateOffer] = "destination must not be equal to account."
        if self.owner is not None and self.owner == self.account:
            errors[NFTokenCreateOffer] = "owner must not be equal to account."
        # This check is only applicable if the flag belongs to the `flags` field inherited from base Transaction.
        # For other cases such as `set_flag` or `clear_flag` field in account_info transaction, please fix accordingly.
        if (
            not self.has_flag(NFTokenCreateOfferFlag.TF_SELL_NFTOKEN) and
            self.owner is None
        ):
            errors["NFTokenCreateOffer"] = "`owner` must be set without flag `TF_SELL_NFTOKEN`"
        # This check is only applicable if the flag belongs to the `flags` field inherited from base Transaction.
        # For other cases such as `set_flag` or `clear_flag` field in account_info transaction, please fix accordingly.
        if (
            self.has_flag(NFTokenCreateOfferFlag.TF_SELL_NFTOKEN) and
            self.owner is not None
        ):
            errors["NFTokenCreateOffer"] = "`owner` must not be set with flag `TF_SELL_NFTOKEN`"
        return errors

class NFTokenCreateOfferFlagInterface(FlagInterface):
    """
    Enum for NFTokenCreateOffer Transaction Flags.
    """

    TF_SELL_NFTOKEN: bool

class NFTokenCreateOfferFlag(int, Enum):
    """
    Enum for NFTokenCreateOffer Transaction Flags.
    """

    TF_SELL_NFTOKEN = 0x00000001
    """
    If enabled, indicates that the offer is a sell offer. Otherwise, it is a buy offer.
    """


