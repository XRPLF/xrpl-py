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
    """
    The identifying (classic) address of this account. This field is required.
    """

    account_txn_id: Optional[str] = None
    """
    The identifying hash of the transaction most recently sent by this account. This
    field must be enabled to use the `AccountTxnID` transaction field. To enable it,
    send an AccountSet transaction with the `asfAccountTxnID` flag enabled.
    """

    amm_id: Optional[str] = None
    """
    The ledger entry ID of the corresponding AMM ledger entry. Set during account
    creation; cannot be modified. If present, indicates that this is a special AMM
    AccountRoot; always omitted on non-AMM accounts.
    """

    balance: str = REQUIRED  # type: ignore
    """
    The account's current XRP balance in drops, represented as a string. This field is
    required.
    """

    burned_nftokens: Optional[int] = None
    """
    How many total of this account's issued non-fungible tokens have been burned. This
    number is always equal or less than `MintedNFTokens`.
    """

    domain: Optional[str] = None
    """
    A domain associated with this account. In JSON, this is the hexadecimal for the
    ASCII representation of the domain. Cannot be more than 256 bytes in length.
    """

    email_hash: Optional[str] = None
    """
    The md5 hash of an email address. Clients can use this to look up an avatar through
    services such as Gravatar.
    """

    first_nftoken_sequence: Optional[int] = None
    """
    The account's Sequence Number at the time it minted its first non-fungible-token.
    """

    message_key: Optional[str] = None
    """
    A public key that may be used to send encrypted messages to this account. In JSON,
    uses hexadecimal. Must be exactly 33 bytes, with the first byte indicating the key
    type: `0x02` or `0x03` for secp256k1 keys, `0xED` for Ed25519 keys.
    """

    minted_nftokens: Optional[int] = None
    """
    How many total non-fungible tokens have been minted by and on behalf of this
    account.
    """

    nftoken_minter: Optional[str] = None
    """
    Another account that can mint non-fungible tokens on behalf of this account.
    """

    owner_count: int = REQUIRED  # type: ignore
    """
    The number of objects this account owns in the ledger, which contributes to its
    owner reserve.
    """

    previous_txn_id: str = REQUIRED  # type: ignore
    """
    The identifying hash of the transaction that most recently modified this object.
    This field is required.
    """

    previous_txn_lgr_seq: int = REQUIRED  # type: ignore
    """
    The index of the ledger that contains the transaction that most recently modified
    this object. This field is required.
    """

    regular_key: Optional[str] = None
    """
    The address of a key pair that can be used to sign transactions for this account
    instead of the master key. Use a `SetRegularKey` transaction to change this value.
    """

    sequence: int = REQUIRED  # type: ignore
    """
    The sequence number of the next valid transaction for this account.
    """

    ticket_count: Optional[int] = None
    """
    How many Tickets this account owns in the ledger. This is updated automatically to
    ensure that the account stays within the hard limit of 250 Tickets at a time. This
    field is omitted if the account has zero Tickets.
    """

    tick_size: Optional[int] = None
    """
    How many significant digits to use for exchange rates of Offers involving
    currencies issued by this address. Valid values are 3 to 15, inclusive.
    """

    transfer_rate: Optional[int] = None
    """
    A transfer fee to charge other users for sending currency issued by this account to
    each other.
    """

    wallet_locator: Optional[str] = None
    """
    An arbitrary 256-bit value that users can set.
    """

    wallet_size: Optional[int] = None
    """
    Unused. (The code supports this field but there is no way to set it.)
    """

    flags: Union[int, AccountRootFlags] = REQUIRED  # type: ignore
    """
    A bit-map of boolean flags. This field is required.
    """

    ledger_entry_type: LedgerEntryType = field(
        default=LedgerEntryType.ACCOUNT_ROOT, init=False
    )


class AccountRootFlags(Enum):
    """The flags for the `AccountRoot` Ledger Object"""

    LSF_ALLOW_TRUSTLINE_CLAWBACK = 0x80000000
    LSF_DEFAULT_RIPPLE = 0x00800000
    LSF_DEPOSIT_AUTH = 0x01000000
    LSF_DISABLE_MASTER = 0x00100000
    LSF_DISALLOW_INCOMING_CHECK = 0x08000000
    LSF_DISALLOW_INCOMING_NFTOKEN_OFFER = 0x04000000
    LSF_DISALLOW_INCOMING_PAY_CHAN = 0x10000000
    LSF_DISALLOW_INCOMING_TRUSTLINE = 0x20000000
    LSF_DISALLOW_XRP = 0x00080000
    LSF_GLOBAL_FREEZE = 0x00400000
    LSF_NO_FREEZE = 0x00200000
    LSF_PASSWORD_SPENT = 0x00010000
    LSF_REQUIRE_AUTH = 0x00040000
    LSF_REQUIRE_DEST_TAG = 0x00020000
