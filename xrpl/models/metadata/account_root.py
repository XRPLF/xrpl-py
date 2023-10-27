"""Models for the Metadata Object `AccountRoot`"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Union

from xrpl.models.ledger_objects import AccountRootFlags
from xrpl.models.ledger_objects.ledger_object import LedgerObject
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class AccountRoot(LedgerObject):
    """
    The model for the `AccountRoot` Ledger Object when
    represented in a transaction's metadata.
    """

    account: Optional[str] = None
    balance: Optional[str] = None
    flags: Optional[Union[int, AccountRootFlags]] = None
    owner_count: Optional[int] = None
    previous_txn_id: Optional[str] = None
    previous_txn_lgr_seq: Optional[int] = None
    sequence: Optional[int] = None
    account_txn_id: Optional[str] = None
    burned_nftokens: Optional[int] = None
    domain: Optional[str] = None
    email_hash: Optional[str] = None
    message_key: Optional[str] = None
    minted_nftokens: Optional[int] = None
    nftoken_minter: Optional[str] = None
    regular_key: Optional[str] = None
    ticket_count: Optional[int] = None
    ticket_size: Optional[int] = None
    transfer_rate: Optional[int] = None
    wallet_locator: Optional[str] = None
    wallet_size: Optional[int] = None
