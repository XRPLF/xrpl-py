"""
The ledger_entry method returns a single ledger
object from the XRP Ledger in its raw format.
See ledger format for information on the
different types of objects you can retrieve.
`See ledger entry <https://xrpl.org/ledger_entry.html>`_
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union

from xrpl.models.base_model import BaseModel
from xrpl.models.requests.request import Request, RequestMethod
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class DepositPreauth(BaseModel):
    """
    Required fields for requesting a DepositPreauth if not querying by
    object ID.
    """

    owner: str = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """

    authorized: str = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """


@require_kwargs_on_init
@dataclass(frozen=True)
class Directory(BaseModel):
    """
    Required fields for requesting a DirectoryNode if not querying by
    object ID.
    """

    owner: str = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """

    dir_root: str = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """
    sub_index: Optional[int] = None


@require_kwargs_on_init
@dataclass(frozen=True)
class Escrow(BaseModel):
    """
    Required fields for requesting a Escrow if not querying by
    object ID.
    """

    owner: str = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """

    seq: int = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """


@require_kwargs_on_init
@dataclass(frozen=True)
class Offer(BaseModel):
    """
    Required fields for requesting a Offer if not querying by
    object ID.
    """

    account: str = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """

    seq: int = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """


@require_kwargs_on_init
@dataclass(frozen=True)
class RippleState(BaseModel):
    """Required fields for requesting a RippleState."""

    accounts: List[str] = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """

    currency: str = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """


@require_kwargs_on_init
@dataclass(frozen=True)
class Ticket(BaseModel):
    """
    Required fields for requesting a Ticket, if not querying by
    object ID.
    """

    owner: str = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """

    ticket_sequence: int = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """


@require_kwargs_on_init
@dataclass(frozen=True)
class LedgerEntry(Request):
    """
    The ledger_entry method returns a single ledger
    object from the XRP Ledger in its raw format.
    See ledger format for information on the
    different types of objects you can retrieve.
    `See ledger entry <https://xrpl.org/ledger_entry.html>`_
    """

    method: RequestMethod = field(default=RequestMethod.LEDGER_ENTRY, init=False)
    index: Optional[str] = None
    account_root: Optional[str] = None
    check: Optional[str] = None
    deposit_preauth: Optional[Union[str, DepositPreauth]] = None
    directory: Optional[Union[str, Directory]] = None
    escrow: Optional[Union[str, Escrow]] = None
    offer: Optional[Union[str, Offer]] = None
    payment_channel: Optional[str] = None
    ripple_state: Optional[RippleState] = None
    ticket: Optional[Union[str, Ticket]] = None
    binary: bool = False
    ledger_hash: Optional[str] = None
    ledger_index: Optional[Union[str, int]] = None

    def _get_errors(self: LedgerEntry) -> Dict[str, str]:
        errors = super()._get_errors()
        query_params = [
            param
            for param in [
                self.index,
                self.account_root,
                self.directory,
                self.offer,
                self.ripple_state,
                self.check,
                self.escrow,
                self.payment_channel,
                self.deposit_preauth,
                self.ticket,
            ]
            if param is not None
        ]
        if len(query_params) != 1:
            errors["LedgerEntry"] = "Must choose exactly one data to query"
        return errors
