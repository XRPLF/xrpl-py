"""
The base class for all network response types.
Represents fields common to all response types.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from xrpl.models.base_model import BaseModel


class ResponseStatus(str, Enum):
    """TODO: docstring"""

    SUCCESS = "success"


class ResponseType(str, Enum):
    """TODO: docstring"""

    RESPONSE = "response"
    LEDGER_CLOSED = "ledgerClosed"
    TRANSACTION = "transaction"


@dataclass(frozen=True)
class Response(BaseModel):
    """
    The base class for all network response types.
    Represents fields common to all response types.
    """

    status: ResponseStatus
    result: Union[List[Any], Dict[Any]]
    id: Optional[Union[int, str]] = None
    type: Optional[ResponseType] = None

    def is_successful(self):
        """TODO: docstring"""
        return self.status == ResponseStatus.SUCCESS
