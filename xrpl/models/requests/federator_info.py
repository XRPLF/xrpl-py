"""
The server_info command asks the server for a
human-readable version of various information
about the rippled server being queried.
"""
from dataclasses import dataclass, field

from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class FederatorInfo(Request):
    """
    The federator_info command asks the federator for a
    human-readable version of various information
    about the federator being queried.
    """

    method: RequestMethod = field(default=RequestMethod.FEDERATOR_INFO, init=False)
