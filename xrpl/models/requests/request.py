"""
The base class for all network request types.
Represents fields common to all request types.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Type, TypeVar, Union, cast

import xrpl.models.requests  # bare import to get around circular dependency
from xrpl.models.base_model import BaseModel
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


class RequestMethod(str, Enum):
    """Represents the different options for the ``method`` field in a request."""

    # account methods
    ACCOUNT_CHANNELS = "account_channels"
    ACCOUNT_CURRENCIES = "account_currencies"
    ACCOUNT_INFO = "account_info"
    ACCOUNT_LINES = "account_lines"
    ACCOUNT_NFTS = "account_nfts"
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

    # NFT methods
    NFT_BUY_OFFERS = "nft_buy_offers"
    NFT_SELL_OFFERS = "nft_sell_offers"

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

    # sidechain methods
    FEDERATOR_INFO = "federator_info"

    # generic unknown/unsupported request
    # (there is no XRPL analog, this model is specific to xrpl-py)
    GENERIC_REQUEST = "zzgeneric_request"


R = TypeVar("R", bound="Request")


@require_kwargs_on_init
@dataclass(frozen=True)
class Request(BaseModel):
    """
    The base class for all network request types.
    Represents fields common to all request types.
    """

    method: RequestMethod = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """

    id: Optional[Union[str, int]] = None

    @classmethod
    def from_dict(cls: Type[R], value: Dict[str, Any]) -> R:
        """
        Construct a new Request from a dictionary of parameters.

        Args:
            value: The value to construct the Request from.

        Returns:
            A new Request object, constructed using the given parameters.

        Raises:
            XRPLModelException: If the dictionary provided is invalid.
        """
        if cls.__name__ == "Request":
            if "method" not in value:
                raise XRPLModelException("Request does not include method.")
            correct_type = cls.get_method(value["method"])
            return correct_type.from_dict(value)  # type: ignore

        if "method" in value:
            method = value["method"]
            if (
                cls.get_method(method).__name__ != cls.__name__
                and not (
                    method == "submit"
                    and cls.__name__ in ("SignAndSubmit", "SubmitOnly")
                )
                and not cls.__name__ == "GenericRequest"
            ):
                raise XRPLModelException(
                    f"Using wrong constructor: using {cls.__name__} constructor "
                    f"with Request method {method}."
                )
            value = {**value}
            del value["method"]

        return super(Request, cls).from_dict(value)

    @classmethod
    def get_method(cls: Type[Request], method: str) -> Type[Request]:
        """
        Returns the correct request method based on the string name.

        Args:
            method: The String name of the Request object.

        Returns:
            The request class with the given name. If the request doesn't exist, then
            it will return a `GenericRequest`.
        """
        # special case for NoRippleCheck and NFT methods
        if method == RequestMethod.NO_RIPPLE_CHECK:
            return xrpl.models.requests.NoRippleCheck
        if method == RequestMethod.ACCOUNT_NFTS:
            return xrpl.models.requests.AccountNFTs
        if method == RequestMethod.NFT_BUY_OFFERS:
            return xrpl.models.requests.NFTBuyOffers
        if method == RequestMethod.NFT_SELL_OFFERS:
            return xrpl.models.requests.NFTSellOffers

        parsed_name = "".join([word.capitalize() for word in method.split("_")])
        if parsed_name in xrpl.models.requests.__all__:
            return cast(Type[Request], getattr(xrpl.models.requests, parsed_name))
        return xrpl.models.requests.GenericRequest

    def to_dict(self: Request) -> Dict[str, Any]:
        """
        Returns the dictionary representation of a Request.

        Returns:
            The dictionary representation of a Request.
        """
        # we need to override this because method is using ``field``
        # which will not include the value in the object's __dict__
        return {**super().to_dict(), "method": self.method.value}
