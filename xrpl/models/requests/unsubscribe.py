"""
The unsubscribe command tells the server to stop sending
messages for a particular subscription or set of subscriptions.

WebSocket API only.
"""
from dataclasses import dataclass
from typing import Any, List, Optional

from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.requests.subscribe import StreamParameter


@dataclass(frozen=True)
class Unsubscribe(Request):
    """
    The unsubscribe command tells the server to stop sending
    messages for a particular subscription or set of subscriptions.

    WebSocket API only.
    """

    method: RequestMethod = RequestMethod.UNSUBSCRIBE
    streams: Optional[List[StreamParameter]] = None
    accounts: Optional[List[str]] = None
    accounts_proposed: Optional[List[str]] = None
    # TODO need type
    books: Optional[List[Any]] = None
