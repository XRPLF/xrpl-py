"""Model for OfferEntry."""
from dataclasses import dataclass
from typing import Optional, Union
from xrpl.models.base_model import BaseModel
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class OfferEntry(BaseModel):
    """
    Retrieve an Offer entry, which defines an offer to exchange currency.
    """

    offer: Optional[Union[str, OfferEntryOfferOneOf]] = None

