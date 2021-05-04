"""
The base class for all network request types.
Represents fields common to all request types.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Type, Union, cast

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


def _snake_to_camel(snake: str) -> str:
    if snake == "noripple_check":
        return "NoRippleCheck"
    snaked = "".join([word.capitalize() for word in snake.split("_")])
    return re.sub(r"Unl", r"UNL", re.sub(r"Id", r"ID", snaked))


@require_kwargs_on_init
@dataclass(frozen=True)
class Request(BaseModel):
    """
    The base class for all network request types.
    Represents fields common to all request types.
    """

    method: RequestMethod = REQUIRED  # type: ignore
    id: Optional[Union[str, int]] = None

    def to_dict(self: Request) -> Dict[str, Any]:
        """
        Returns the dictionary representation of a Request.

        Returns:
            The dictionary representation of a Request.
        """
        # we need to override this because method is using ``field``
        # which will not include the value in the objects __dict__
        return {**super().to_dict(), "method": self.method.value}

    @classmethod
    def from_dict(cls: Type[Request], value: Dict[str, Any]) -> Request:
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
            return correct_type.from_dict(value)
        else:
            if "method" in value:
                method = value["method"]
                if _snake_to_camel(method) != cls.__name__ and not (
                    method == "submit"
                    and (cls.__name__ in {"SignAndSubmit", "SubmitOnly"})
                ):
                    raise XRPLModelException(
                        f"Using wrong constructor: using {cls.__name__} constructor "
                        f"with Request type {method}."
                    )
                value = {**value}
                del value["method"]
            return cast(Request, super(Request, cls).from_dict(value))

    @classmethod
    def get_method(cls: Type[Request], method: str) -> Type[Request]:
        """
        Returns the correct Request method based on the string name.

        Args:
            method: The String name of the Request object.

        Returns:
            The Request class with the given name.

        Raises:
            XRPLModelException: If `method` is not a valid Request type.
        """
        import xrpl.models.requests as request_models

        request_methods: Dict[str, Type[Request]] = {}
        for req in RequestMethod:
            req_model_name = _snake_to_camel(req.value)
            request_methods[req.value] = getattr(request_models, req_model_name)
        if method in request_methods:
            return request_methods[method]

        raise XRPLModelException(f"{method} is not a valid Request method")
