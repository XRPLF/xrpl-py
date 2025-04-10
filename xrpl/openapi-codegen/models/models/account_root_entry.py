"""Model for AccountRootEntry."""
from dataclasses import dataclass
from typing import Optional
from xrpl.models.base_model import BaseModel
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class AccountRootEntry(BaseModel):
    """
    Retrieve an AccountRoot entry by its address. This is roughly equivalent to the
    account_info method.
    """

    account_root: Optional[str] = None
    """
    The classic address of the AccountRoot entry to retrieve.
    """


