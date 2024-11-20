"""
This request returns the raw ledger format for all objects owned by an account.

For a higher-level view of an account's trust lines and balances, see
AccountLinesRequest instead.

`See account_objects <https://xrpl.org/account_objects.html>`_
"""

from dataclasses import dataclass, field
from typing import Any, Optional

from xrpl.models.requests.ledger_entry import LedgerEntryType
from xrpl.models.requests.request import LookupByLedgerRequest, Request, RequestMethod
from xrpl.models.required import REQUIRED
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class AccountObjects(Request, LookupByLedgerRequest):
    """
    This request returns the raw ledger format for all objects owned by an account.

    For a higher-level view of an account's trust lines and balances, see
    AccountLinesRequest instead.

    `See account_objects <https://xrpl.org/account_objects.html>`_
    """

    account: str = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """

    method: RequestMethod = field(default=RequestMethod.ACCOUNT_OBJECTS, init=False)
    type: Optional[LedgerEntryType] = None
    deletion_blockers_only: bool = False
    limit: Optional[int] = None
    # marker data shape is actually undefined in the spec, up to the
    # implementation of an individual server
    marker: Optional[Any] = None
