"""
The subscribe method requests periodic notifications from the server
when certain events happen.

WebSocket API only.
"""
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from xrpl.models.base_model import REQUIRED, BaseModel
from xrpl.models.currencies import Currency
from xrpl.models.requests.request import Request, RequestMethod


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


@dataclass(frozen=True)
class SubscribeBook(BaseModel):
    """Format for elements in the `books` array for Subscribe only."""

    taker_gets: Currency = REQUIRED
    taker_pays: Currency = REQUIRED
    taker: str = REQUIRED
    snapshot: Optional[bool] = False
    both: Optional[bool] = False


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
    books: Optional[List[SubscribeBook]] = None
    url: Optional[str] = None
    url_username: Optional[str] = None
    url_password: Optional[str] = None
