"""Model for AMMEntryAmmOneOf."""
from dataclasses import dataclass
from xrpl.models.base_model import BaseModel
from xrpl.models.utils import REQUIRED
from xrpl.models.issued_currency import IssuedCurrency
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class AMMEntryAmmOneOf(BaseModel):
    asset: IssuedCurrency = REQUIRED
    asset2: IssuedCurrency = REQUIRED

