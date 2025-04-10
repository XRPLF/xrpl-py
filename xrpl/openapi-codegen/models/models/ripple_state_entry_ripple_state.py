"""Model for RippleStateEntryRippleState."""
from dataclasses import dataclass
from typing import List
from xrpl.models.base_model import BaseModel
from xrpl.models.utils import REQUIRED
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class RippleStateEntryRippleState(BaseModel):
    accounts: List[str] = REQUIRED
    currency: str = REQUIRED
    def _get_errors(self: RippleStateEntryRippleState) -> Dict[str, str]:
        errors = super._get_errors()
        if self.accounts is not None and len(self.accounts) < 2:
            errors["RippleStateEntryRippleState"] = "Field `accounts` must have a length greater than or equal to 2"
        if self.accounts is not None and len(self.accounts) > 2:
            errors["RippleStateEntryRippleState"] = "Field `accounts` must have a length less than or equal to 2"
        return errors


