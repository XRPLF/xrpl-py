"""Model for AuthorizeCredentials."""
from dataclasses import dataclass
from xrpl.models.base_model import BaseModel
from xrpl.models.utils import REQUIRED
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class AuthorizeCredentials(BaseModel):
    """
    Represents a credential used for preauthorization.
    """

    issuer: str = REQUIRED
    """
    (Required) The issuer of the credential.
    """

    credential_type: str = REQUIRED
    """
    (Required) The credential type of the credential.
    """


