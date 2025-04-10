"""Model for ServerInfo request type."""
from dataclasses import dataclass, field
from typing import Optional
from xrpl.models.base_model import BaseModel
from xrpl.models.requests.request import RequestMethod
from xrpl.models.utils import require_kwargs_on_init

@require_kwargs_on_init
@dataclass(frozen=True)
class ServerInfo(BaseModel):
    """
    The server_info command asks the server for a human-readable version of various
    information about the rippled server being queried.
    """

    method: RequestMethod = field(default=RequestMethod.SERVER_INFO, init=False)

    counters: Optional[bool] = None
    """
    If true, return metrics about the job queue, ledger store, and API method activity. The
    default is false.
    """


