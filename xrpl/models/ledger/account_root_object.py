"""
Represents the AccountRoot ledger object, which describes a single account,
its settings, and XRP balance.

See https://xrpl.org/accountroot.html.
"""
from dataclasses import dataclass, field
from typing import List, Optional

from xrpl.models.ledger.ledger_object import LedgerObject, LedgerObjectType


@dataclass(frozen=True)
class AccountRootObject(LedgerObject):
    """
    Represents the AccountRoot ledger object, which describes a single account,
    its settings, and XRP balance.

    Attributes:
        account: The account
        balance: The balance
        flags: The flags
        index: The index
        owner_count: The owner count
        previous_transaction_id: The previous transaction id
        previous_transaction_ledger_sequence; The previous transaction sequence
        sequence: The sequence
        account_transaction_id: The id
        domain: The domain
        email_hash: The email hash
        message_key: The message key
        regular_key: The key
        signer_lists: The list of signers
        tick_size: The tick size
        transfer_rate: The transfer rate
    """

    type: LedgerObjectType = field(
        default_factory=lambda: LedgerObjectType.AccountRoot, init=False
    )

    # TODO: Use Address type
    account: str
    # TODO: Use XrpCurrencyAmount type
    balance: str
    flags: int
    # TODO: Use Hash256 type
    index: str
    owner_count: int
    # TODO: Use Hash256 type
    previous_transaction_id: str
    previous_transaction_ledger_sequence: int
    sequence: int
    # TODO: Use Hash256 type
    account_transaction_id: Optional[str] = None
    domain: Optional[str] = None
    email_hash: Optional[str] = None
    message_key: Optional[str] = None
    # TODO: Use Address type
    regular_key: Optional[str] = None
    # TODO: Use SignerListObject once implemented
    signer_lists: Optional[List] = None
    tick_size: Optional[int] = None
    transfer_rate: Optional[int] = None
