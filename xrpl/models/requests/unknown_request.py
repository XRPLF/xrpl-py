"""A generic request that can be used for unsupported requests."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Type

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(init=False, frozen=True)
class UnknownRequest(Request):
    """A request object representing all unsupported requests."""

    method: RequestMethod = field(default=RequestMethod.UNKNOWN_REQUEST, init=False)
    """
    This field is required.

    :meta hide-value:
    """

    def __init__(self: UnknownRequest, **kwargs: Dict[str, Any]) -> None:
        super().__init__(
            id=(kwargs["id"] if "id" in kwargs else None),
            method=RequestMethod.UNKNOWN_REQUEST,
        )
        for key, value in kwargs.items():
            print(key, value)
            object.__setattr__(self, key, value)

    @classmethod
    def from_dict(cls: Type[UnknownRequest], value: Dict[str, Any]) -> None:
        """
        Called by dataclasses immediately after __init__. Reshapes the request from
        JSON/WS formatting to the internal formatting used by requests.
        """
        if "command" in value:  # websocket formatting
            value["method"] = value["command"]
            del value["command"]

        elif "method" in value:  # JSON RPC formatting
            if "params" in value:  # actual JSON RPC formatting
                value = {"method": value["method"], **value["params"]}
            # else is the internal request formatting

        else:
            raise XRPLModelException("Must have a command or a method in a request")

        return cls(**value)

    def to_dict(self: Request) -> Dict[str, Any]:
        """
        Returns the dictionary representation of a Request.

        Returns:
            The dictionary representation of a Request.
        """
        return {
            key: self._to_dict_elem(getattr(self, key))
            for key in self.__dict__
            if getattr(self, key) is not None
        }
