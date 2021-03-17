"""
The base class for all network request types.
Represents fields common to all request types.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

from xrpl.models.base_model import BaseModel
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


class RequestMethod(str, Enum):
    """Represents the different options for the ``method`` field in a request."""

    # account methods
    ACCOUNT_CHANNELS = "account_channels"
    ACCOUNT_CURRENCIES = "account_currencies"
    ACCOUNT_INFO = "account_info"
    ACCOUNT_LINES = "account_lines"
    ACCOUNT_OBJECTS = "account_objects"
    ACCOUNT_OFFERS = "account_offers"
    ACCOUNT_TX = "account_tx"
    GATEWAY_BALANCES = "gateway_balances"
    NO_RIPPLE_CHECK = "noripple_check"

    # transaction methods
    SIGN = "sign"
    SIGN_FOR = "sign_for"
    SUBMIT = "submit"
    SUBMIT_MULTISIGNED = "submit_multisigned"
    TRANSACTION_ENTRY = "transaction_entry"
    TX = "tx"

    # channel methods
    CHANNEL_AUTHORIZE = "channel_authorize"
    CHANNEL_VERIFY = "channel_verify"

    # path methods
    BOOK_OFFERS = "book_offers"
    DEPOSIT_AUTHORIZED = "deposit_authorized"
    PATH_FIND = "path_find"
    RIPPLE_PATH_FIND = "ripple_path_find"

    # ledger methods
    LEDGER = "ledger"
    LEDGER_CLOSED = "ledger_closed"
    LEDGER_CURRENT = "ledger_current"
    LEDGER_DATA = "ledger_data"
    LEDGER_ENTRY = "ledger_entry"

    # subscription methods
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"

    # server info methods
    FEE = "fee"
    MANIFEST = "manifest"
    SERVER_INFO = "server_info"
    SERVER_STATE = "server_state"

    # utility methods
    PING = "ping"
    RANDOM = "random"


@require_kwargs_on_init
@dataclass(frozen=True)
class Request(BaseModel):
    """
    The base class for all network request types.
    Represents fields common to all request types.
    """

    method: RequestMethod = REQUIRED  # type: ignore
    id: Optional[int] = None

    def to_dict(self: Request) -> Dict[str, Any]:
        """
        Returns the dictionary representation of a Request.

        Returns:
            The dictionary representation of a Request.
        """
        # we need to override this because method is using ``field``
        # which will not include the value in the objects __dict__
        return {**super().to_dict(), "method": self.method.value}
