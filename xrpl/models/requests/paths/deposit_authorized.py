"""
The deposit_authorized command indicates whether one account
is authorized to send payments directly to another. See
Deposit Authorization for information on how to require
authorization to deliver money to your account.
"""
from dataclasses import dataclass
from typing import Optional

from xrpl.models.base_model import REQUIRED
from xrpl.models.requests.request import Request, RequestMethod


@dataclass(frozen=True)
class DepositAuthorized(Request):
    """
    The deposit_authorized command indicates whether one account
    is authorized to send payments directly to another. See
    Deposit Authorization for information on how to require
    authorization to deliver money to your account.
    """

    source_account: str = REQUIRED  # type: ignore
    destination_account: str = REQUIRED  # type: ignore
    method: RequestMethod = RequestMethod.DEPOSIT_AUTHORIZED
    ledger_hash: Optional[str] = None
    ledger_index: Optional[str] = None
