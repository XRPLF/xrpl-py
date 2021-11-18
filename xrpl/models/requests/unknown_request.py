"""A generic request that can be used for unsupported requests."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Type

from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class UnknownRequest(Request):
    """
    The tx method retrieves information on a single transaction.

    `See tx <https://xrpl.org/tx.html>`_
    """

    method: RequestMethod = field(default=RequestMethod.UNKNOWN, init=False)
    request: Dict[str, Any] = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """

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
        return self.request
