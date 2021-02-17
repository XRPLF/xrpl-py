"""
The base class for all network request types. Represents fields common to all request
types.


"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Enum

from xrpl.models.base_model import BaseModel


class RequestMethod(str, Enum):
    """TODO: docstring"""

    # account methods
    AccountChannels = "account_channels"
    AccountCurrencies = "account_currencies"
    AccountInfo = "account_info"
    AccountLines = "account_lines"
    AccountObjects = "account_objects"
    AccountOffers = "account_offers"
    AccountTransactions = "account_tx"
    GatewayBalances = "gateway_balances"
    NoRippleCheck = "noripple_check"


@dataclass(frozen=True)
class Request(BaseModel):
    """TODO: docstring"""

    method: RequestMethod = field(init=False)
