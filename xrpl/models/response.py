"""
The base class for all network response types.

Represents fields common to all response types.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from xrpl.models.base_model import REQUIRED, BaseModel
from xrpl.models.utils import require_kwargs_on_init


class ResponseStatus(str, Enum):
    """Represents the different status possibilities."""

    SUCCESS = "success"
    ERROR = "error"


class ResponseType(str, Enum):
    """Represents the different response types a Response can have."""

    RESPONSE = "response"
    LEDGER_CLOSED = "ledgerClosed"
    TRANSACTION = "transaction"


@require_kwargs_on_init
@dataclass(frozen=True)
class Response(BaseModel):
    """
    The base class for all network response types.

    Represents fields common to all response types.
    """

    status: ResponseStatus = REQUIRED
    result: Union[List[Any], Dict[Any]] = REQUIRED
    id: Optional[Union[int, str]] = None
    type: Optional[ResponseType] = None

    def is_successful(self: Response) -> bool:
        """
        Returns whether the request was successfully received and understood by the
        server.

        Returns:
            Whether the request was successfully received and understood by the server.
        """
        return self.status == ResponseStatus.SUCCESS
