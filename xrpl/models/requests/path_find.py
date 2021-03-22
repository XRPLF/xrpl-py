"""
WebSocket API only! The path_find method searches for a
path along which a transaction can possibly be made, and
periodically sends updates when the path changes over time.
For a simpler version that is supported by JSON-RPC, see the
ripple_path_find method. For payments occurring strictly in XRP,
it is not necessary to find a path, because XRP can be sent
directly to any account.

There are three different modes, or sub-commands, of the path_find
command. Specify which one you want with the subcommand parameter:

create - Start sending pathfinding information
close - Stop sending pathfinding information
status - Get the information of the currently-open pathfinding request
Although the rippled server tries to find the cheapest path or combination
of paths for making a payment, it is not guaranteed that the paths returned
by this method are, in fact, the best paths. Due to server load,
pathfinding may not find the best results. Additionally, you should be
careful with the pathfinding results from untrusted servers. A server
could be modified to return less-than-optimal paths to earn money for its
operators. If you do not have your own server that you can trust with
pathfinding, you should compare the results of pathfinding from multiple
servers run by different parties, to minimize the risk of a single server
returning poor results. (Note: A server returning less-than-optimal
results is not necessarily proof of malicious behavior; it could also be
a symptom of heavy server load.)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from xrpl.models.amounts import Amount
from xrpl.models.base_model import BaseModel
from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


class PathFindSubcommand(str, Enum):
    """
    There are three different modes, or sub-commands, of the path_find
    command. Specify which one you want with the subcommand parameter:

    create - Start sending pathfinding information
    close - Stop sending pathfinding information
    status - Get the information of the currently-open pathfinding request
    """

    CREATE = "create"
    CLOSE = "close"
    STATUS = "status"


@require_kwargs_on_init
@dataclass(frozen=True)
class PathStep(BaseModel):
    """
    A path set is an array. Each member of the path set is another array that
    represents an individual path. Each member of a path is an object that
    specifies the step. A step has the following fields.
    """

    account: Optional[str] = None
    currency: Optional[str] = None
    issuer: Optional[str] = None
    type: Optional[int] = None
    type_hex: Optional[str] = None

    def _get_errors(self: PathStep) -> Dict[str, str]:
        return {
            key: value
            for key, value in {
                **super()._get_errors(),
                "account": self._get_account_error(),
                "currency": self._get_currency_error(),
                "issuer": self._get_issuer_error(),
            }.items()
            if value is not None
        }

    def _get_account_error(self: PathStep) -> Optional[str]:
        if self.account is None:
            return None
        if self.currency is not None or self.issuer is not None:
            return "Cannot set account if currency or issuer are set"
        return None

    def _get_currency_error(self: PathStep) -> Optional[str]:
        if self.currency is None:
            return None
        if self.account is not None:
            return "Cannot set currency if account is set"
        if self.issuer is not None and self.currency.upper() == "XRP":
            return "Cannot set issuer if currency is XRP"
        return None

    def _get_issuer_error(self: PathStep) -> Optional[str]:
        if self.issuer is None:
            return None
        if self.account is not None:
            return "Cannot set issuer if account is set"
        if self.currency is not None and self.currency.upper() == "XRP":
            return "Cannot set issuer if currency is XRP"
        return None


@require_kwargs_on_init
@dataclass(frozen=True)
class PathFind(Request):
    """
    WebSocket API only! The path_find method searches for a
    path along which a transaction can possibly be made, and
    periodically sends updates when the path changes over time.
    For a simpler version that is supported by JSON-RPC, see the
    ripple_path_find method. For payments occurring strictly in XRP,
    it is not necessary to find a path, because XRP can be sent
    directly to any account.

    Although the rippled server tries to find the cheapest path or combination
    of paths for making a payment, it is not guaranteed that the paths returned
    by this method are, in fact, the best paths. Due to server load,
    pathfinding may not find the best results. Additionally, you should be
    careful with the pathfinding results from untrusted servers. A server
    could be modified to return less-than-optimal paths to earn money for its
    operators. If you do not have your own server that you can trust with
    pathfinding, you should compare the results of pathfinding from multiple
    servers run by different parties, to minimize the risk of a single server
    returning poor results. (Note: A server returning less-than-optimal
    results is not necessarily proof of malicious behavior; it could also be
    a symptom of heavy server load.)
    """

    #: This field is required.
    subcommand: PathFindSubcommand = REQUIRED  # type: ignore
    #: This field is required.
    source_account: str = REQUIRED  # type: ignore
    #: This field is required.
    destination_account: str = REQUIRED  # type: ignore
    #: This field is required.
    destination_amount: Amount = REQUIRED  # type: ignore
    method: RequestMethod = field(default=RequestMethod.PATH_FIND, init=False)
    send_max: Optional[Amount] = None
    paths: Optional[List[List[PathStep]]] = None
