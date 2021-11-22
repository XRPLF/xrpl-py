"""A generic request that can be used for unsupported requests."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Type

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class UnknownRequest(Request):
    """A request object representing all unsupported requests."""

    method: RequestMethod = field(default=RequestMethod.UNKNOWN_REQUEST, init=False)
    request: Dict[str, Any] = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """

    def __post_init__(self: UnknownRequest) -> None:
        """
        Called by dataclasses immediately after __init__. Reshapes the request from
        JSON/WS formatting to the internal formatting used by requests.
        """
        super(Request, self).__post_init__()
        re_init = False
        value = self.request
        req_id = self.id
        if "id" in value:
            re_init = True
            req_id = value["id"]
            del value["id"]

        if "command" in value:  # websocket formatting
            re_init = True
            value["method"] = value["command"]
            del value["command"]

        elif "method" in value:  # JSON RPC formatting
            if "params" in value:  # actual JSON RPC formatting
                re_init = True
                value = {"method": value["method"], **value["params"]}
            # else is the internal request formatting

        else:
            raise XRPLModelException("Must have a command or a method in a request")

        if re_init:
            self.__init__(id=req_id, request=value)  # type: ignore

    @classmethod
    def from_dict(cls: Type[UnknownRequest], value: Dict[str, Any]) -> UnknownRequest:
        """
        Construct a new UnknownRequest from a dictionary of parameters.

        Args:
            value: The value to construct the UnknownRequest from.

        Returns:
            A new UnknownRequest object, constructed using the given parameters.

        Raises:
            XRPLModelException: If the dictionary provided is invalid.
        """
        return cls(request=value)

    def to_dict(self: UnknownRequest) -> Dict[str, Any]:
        """
        Returns the dictionary representation of a Request.

        Returns:
            The dictionary representation of a Request.
        """
        return {**self.request, "id": self.id}
