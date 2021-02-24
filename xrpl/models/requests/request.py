"""
The base class for all network request types.
Represents fields common to all request types.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from xrpl.models.base_model import BaseModel


class RequestMethod(str, Enum):
    """Represents the different options for the `method` field in a request."""

    # account methods
    ACCOUNT_CHANNELS = "account_channels"
    ACCOUNT_CURRENCIES = "account_currencies"
    ACCOUNT_INFO = "account_info"
    ACCOUNT_LINES = "account_lines"
    ACCOUNT_OBJECTS = "account_objects"
    ACCOUNT_OFFERS = "account_offers"
    ACCOUNT_TRANSACTIONS = "account_tx"
    GATEWAY_BALANCES = "gateway_balances"
    NO_RIPPLE_CHECK = "noripple_check"


@dataclass(frozen=True)
class Request(BaseModel):
    """
    The base class for all network request types.
    Represents fields common to all request types.
    """

    method: RequestMethod = field(init=False)
