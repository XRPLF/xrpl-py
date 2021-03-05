"""
The ping command returns an acknowledgement, so that
clients can test the connection status and latency.
"""
from dataclasses import dataclass

from xrpl.models.requests import Request, RequestMethod


@dataclass(frozen=True)
class Ping(Request):
    """
    The ping command returns an acknowledgement, so that
    clients can test the connection status and latency.
    """

    method: RequestMethod = RequestMethod.PING
