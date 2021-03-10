"""
The ping command returns an acknowledgement, so that
clients can test the connection status and latency.
"""
from dataclasses import dataclass, field

from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class Ping(Request):
    """
    The ping command returns an acknowledgement, so that
    clients can test the connection status and latency.
    """

    method: RequestMethod = field(default=RequestMethod.PING, init=False)
