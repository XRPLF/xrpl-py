"""
The server_info command asks the server for a
human-readable version of various information
about the rippled server being queried.
"""

from dataclasses import dataclass, field
from typing import Optional

from xrpl.models.requests.request import Request, RequestMethod


@dataclass(frozen=True, kw_only=True)
class ServerDefinitions(Request):
    """
    The definitions command asks the server for a
    human-readable version of various information
    about the rippled server being queried.
    """

    method: RequestMethod = field(default=RequestMethod.SERVER_DEFINITIONS, init=False)

    hash: Optional[str] = None
