"""
The subscribe method requests periodic notifications from the server
when certain events happen.

WebSocket API only.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Any, List, Optional

from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.utils import require_kwargs_on_init


class StreamParameter(str, Enum):
    """Represents possible values of the streams query param for subscribe."""

    CONSENSUS = "consensus"
    LEDGER = "ledger"
    MANIFESTS = "manifests"
    PEER_STATUS = "peer_status"
    TRANSACTIONS = "transactions"
    TRANSACTIONS_PROPOSED = "transactions_proposed"
    SERVER = "server"
    VALIDATIONS = "validations"


@require_kwargs_on_init
@dataclass(frozen=True)
class Subscribe(Request):
    """
    The subscribe method requests periodic notifications from the server
    when certain events happen.

    WebSocket API only.
    """

    method: RequestMethod = RequestMethod.SUBSCRIBE
    streams: Optional[List[StreamParameter]] = None
    accounts: Optional[List[str]] = None
    accounts_proposed: Optional[List[str]] = None
    # TODO need type
    books: Optional[List[Any]] = None
    url: Optional[str] = None
    url_username: Optional[str] = None
    url_password: Optional[str] = None
