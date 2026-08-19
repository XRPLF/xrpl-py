"""Model for SubmitOnlyMode."""

from dataclasses import dataclass
from typing import Optional
from xrpl.models.base_model import BaseModel
from xrpl.models.utils import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class SubmitOnlyMode(BaseModel):
    """
    A submit-only request for submitting transactions.
    """

    tx_blob: str = REQUIRED
    """
    Hex representation of the signed transaction to submit. Can be a multi-signed
    transaction.
    """

    fail_hard: Optional[bool] = None
    """
    If true, and the transaction fails locally, do not retry or relay the transaction to
    other servers. Default is false.
    """
