"""Model for IssuedCurrency."""
from dataclasses import dataclass
from typing import Optional
from xrpl.models.base_model import BaseModel
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class IssuedCurrency(BaseModel):
    currency: Optional[str] = None
    """
    Arbitrary currency code for the token.
    """

    issuer: Optional[str] = None
    """
    Generally, the account that issues this token. In special cases, this can refer to the
    account that holds the token instead (for example, in a Clawback transaction).
    """

    def _get_errors(self: IssuedCurrency) -> Dict[str, str]:
        errors = super._get_errors()
        return errors


