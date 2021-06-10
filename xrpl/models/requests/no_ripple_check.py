"""
This request provides a quick way to check the status of the Default Ripple field
for an account and the No Ripple flag of its trust lines, compared with the
recommended settings.

`See noripple_check <https://xrpl.org/noripple_check.html>`_
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Union

from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


class NoRippleCheckRole(str, Enum):
    """Represents the options for the address role in a NoRippleCheckRequest."""

    GATEWAY = "gateway"
    USER = "user"


@require_kwargs_on_init
@dataclass(frozen=True)
class NoRippleCheck(Request):
    """
    This request provides a quick way to check the status of the Default Ripple field
    for an account and the No Ripple flag of its trust lines, compared with the
    recommended settings.

    `See noripple_check <https://xrpl.org/noripple_check.html>`_
    """

    account: str = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """

    ledger_hash: Optional[str] = None
    ledger_index: Optional[Union[str, int]] = None
    method: RequestMethod = field(default=RequestMethod.NO_RIPPLE_CHECK, init=False)
    role: NoRippleCheckRole = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """

    transactions: bool = False
    limit: Optional[int] = 300
