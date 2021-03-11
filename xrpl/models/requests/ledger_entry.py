"""
The ledger_entry method returns a single ledger
object from the XRP Ledger in its raw format.
See ledger format for information on the
different types of objects you can retrieve.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union

from xrpl.models.base_model import REQUIRED, BaseModel
from xrpl.models.requests.request import Request, RequestMethod


@dataclass(frozen=True)
class DepositPreauth(BaseModel):
    """
    Required fields for requesting a DepositPreauth if not querying by
    object ID.
    """

    owner: str = REQUIRED
    authorized: str = REQUIRED


@dataclass(frozen=True)
class Directory(BaseModel):
    """
    Required fields for requesting a DirectoryNode if not querying by
    object ID.
    """

    owner: str = REQUIRED
    dir_root: str = REQUIRED
    sub_index: Optional[int] = None


@dataclass(frozen=True)
class Escrow(BaseModel):
    """
    Required fields for requesting a Escrow if not querying by
    object ID.
    """

    owner: str = REQUIRED
    seq: int = REQUIRED


@dataclass(frozen=True)
class Offer(BaseModel):
    """
    Required fields for requesting a Offer if not querying by
    object ID.
    """

    account: str = REQUIRED
    seq: int = REQUIRED


@dataclass(frozen=True)
class RippleState(BaseModel):
    """Required fields for requesting a RippleState."""

    accounts: List[str] = REQUIRED
    currency: str = REQUIRED


@dataclass(frozen=True)
class Ticket(BaseModel):
    """
    Required fields for requesting a Ticketif not querying by
    object ID.
    """

    owner: str = REQUIRED
    ticket_sequence: int = REQUIRED


@dataclass(frozen=True)
class LedgerEntry(Request):
    """
    The ledger_entry method returns a single ledger
    object from the XRP Ledger in its raw format.
    See ledger format for information on the
    different types of objects you can retrieve.
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
    binary: Optional[bool] = False
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
