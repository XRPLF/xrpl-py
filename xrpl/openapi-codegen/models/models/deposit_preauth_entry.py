"""Model for DepositPreauthEntry."""
from dataclasses import dataclass
from typing import Optional, Union
from xrpl.models.base_model import BaseModel
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class DepositPreauthEntry(BaseModel):
    """
    Retrieve a DepositPreauth entry, which tracks preauthorization for payments to accounts
    requiring Deposit Authorization.
    """

    deposit_preauth: Optional[Union[str, DepositPreauthEntryDepositPreauthOneOf]] = None

