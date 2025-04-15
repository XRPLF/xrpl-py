"""Model for NFTokenCancelOffer transaction type."""

from dataclasses import dataclass, field
from typing import List, Optional
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class NFTokenCancelOffer(Transaction):
    """
    The NFTokenCancelOffer transaction can be used to cancel existing token offers created
    using NFTokenCreateOffer.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.NFTOKEN_CANCEL_OFFER, init=False
    )

    nf_token_offers: List[str] = REQUIRED
    """
    An array of IDs of the NFTokenOffer objects to cancel (not the IDs of NFToken objects,
    but the IDs of the NFTokenOffer objects). Each entry must be a different object ID of an
    NFTokenOffer object; the transaction is invalid if the array contains duplicate entries.
    """

    def _get_errors(self: NFTokenCancelOffer) -> Dict[str, str]:
        errors = super._get_errors()
        if self.nf_token_offers is not None and len(self.nf_token_offers) < 1:
            errors["NFTokenCancelOffer"] = (
                "Field `nf_token_offers` must have a length greater than or equal to 1"
            )
        return errors
