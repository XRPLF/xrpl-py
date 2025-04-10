"""Model for OfferEntryOfferOneOf."""

from dataclasses import dataclass
from xrpl.models.base_model import BaseModel
from xrpl.models.utils import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class OfferEntryOfferOneOf(BaseModel):
    account: str = REQUIRED
    seq: int = REQUIRED
