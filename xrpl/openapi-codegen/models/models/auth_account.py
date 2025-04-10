"""Model for AuthAccount."""
from dataclasses import dataclass
from xrpl.models.base_model import BaseModel
from xrpl.models.utils import REQUIRED
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class AuthAccount(BaseModel):
    account: str = REQUIRED
    """
    (Required) The address of the account to authorize.
    """

    def _get_errors(self: AuthAccount) -> Dict[str, str]:
        errors = super._get_errors()
        return errors


