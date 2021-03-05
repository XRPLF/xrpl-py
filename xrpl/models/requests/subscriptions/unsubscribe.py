"""
The unsubscribe command tells the server to stop sending
messages for a particular subscription or set of subscriptions.
"""
from dataclasses import dataclass
from typing import Any, List, Optional

from xrpl.models.requests import Request, RequestMethod
from xrpl.models.requests.subscriptions.subscribe import StreamParameter


@dataclass(frozen=True)
class Unsubscribe(Request):
    """
    The unsubscribe command tells the server to stop sending
    messages for a particular subscription or set of subscriptions.
    """

    method: RequestMethod = RequestMethod.UNSUBSCRIBE
    streams: Optional[List[StreamParameter]] = None
    accounts: Optional[List[str]] = None
    accounts_proposed: Optional[List[str]] = None
    # TODO need type
    books: Optional[List[Any]] = None
