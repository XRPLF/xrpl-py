"""
The server_info command asks the server for a
human-readable version of various information
about the rippled server being queried.
"""
from dataclasses import dataclass, field

from xrpl.models.requests.request import Request, RequestMethod


@dataclass(frozen=True)
class ServerInfo(Request):
    """
    The server_info command asks the server for a
    human-readable version of various information
    about the rippled server being queried.
    """

    method: RequestMethod = field(default=RequestMethod.SERVER_INFO, init=False)
