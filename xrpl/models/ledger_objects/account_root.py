"""Models for the Ledger Object `AccountRoot`"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Union

from xrpl.models.ledger_objects.ledger_entry_type import LedgerEntryType
from xrpl.models.ledger_objects.ledger_object import LedgerObject
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class AccountRoot(LedgerObject):
    """The model for the `AccountRoot` Ledger Object"""

    account: str = REQUIRED  # type: ignore
    balance: str = REQUIRED  # type: ignore
    flags: Union[int, AccountRootFlags] = REQUIRED  # type: ignore
    owner_count: int = REQUIRED  # type: ignore
    previous_txn_id: str = REQUIRED  # type: ignore
    previous_txn_lgr_seq: int = REQUIRED  # type: ignore
    sequence: int = REQUIRED  # type: ignore
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
    ledger_entry_type: LedgerEntryType = field(
        default=LedgerEntryType.ACCOUNT_ROOT, init=False
    )


@require_kwargs_on_init
@dataclass(frozen=True)
class MDAccountRootFields(LedgerObject):
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


class AccountRootFlags(Enum):
    """The flags for the `AccountRoot` Ledger Object"""

    LSF_DEFAULT_RIPPLE = 0x00800000
    LSF_DEPOSIT_AUTH = 0x01000000
    LSF_DISABLE_MASTER = 0x00100000
    LSF_DISALLOW_XRP = 0x00080000
    LSF_GLOBAL_FREEZE = 0x00400000
    LSF_NO_FREEZE = 0x00200000
    LSF_PASSWORD_SPENT = 0x00010000
    LSF_REQUIRE_AUTH = 0x00040000
    LSF_REQUIRE_DEST_TAG = 0x00020000
