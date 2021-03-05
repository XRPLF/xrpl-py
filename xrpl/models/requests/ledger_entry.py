"""
The ledger_entry method returns a single ledger
object from the XRP Ledger in its raw format.
See ledger format for information on the
different types of objects you can retrieve.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Union

from xrpl.models.requests.request import Request, RequestMethod


@dataclass(frozen=True)
class LedgerEntry(Request):
    """
    The ledger_entry method returns a single ledger
    object from the XRP Ledger in its raw format.
    See ledger format for information on the
    different types of objects you can retrieve.
    """

    method: RequestMethod = RequestMethod.LEDGER_ENTRY
    index: Optional[str] = None
    account_root: Optional[str] = None
    check: Optional[str] = None
    # TODO make type
    deposit_preauth: Optional[Any] = None
    # TODO make type
    directory: Optional[Any] = None
    # TODO make type
    escrow: Optional[Any] = None
    # TODO make type
    offer: Optional[Any] = None
    payment_channel: Optional[str] = None
    # TODO make type
    ripple_state: Optional[Any] = None
    # TODO make type
    ticket: Optional[Any] = None
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
