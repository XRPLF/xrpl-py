"""Model for BaseLedgerEntry request type."""

from dataclasses import dataclass, field
from typing import Optional
from xrpl.models.base_model import BaseModel
from xrpl.models.requests.request import RequestMethod
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class BaseLedgerEntry(BaseModel):
    method: RequestMethod = field(default=RequestMethod.LEDGER_ENTRY, init=False)

    binary: Optional[bool] = None
    """
    (Optional) If true, return the requested ledger entry's contents as a hex string in the
    XRP Ledger's binary format. Otherwise, return data in JSON format. The default is false.
    """

    include_deleted: Optional[bool] = None
    """
    (Optional, Clio servers only) If set to true and the queried object has been deleted,
    return its complete data as it was prior to its deletion. If set to false or not
    provided, and the queried object has been deleted, return objectNotFound (current
    behavior).
    """
