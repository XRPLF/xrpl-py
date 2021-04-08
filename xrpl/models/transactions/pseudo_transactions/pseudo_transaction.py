"""The base model for all pseudo-transactions and their nested object types."""

from dataclasses import dataclass, field

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import PseudoTransactionType
from xrpl.models.utils import require_kwargs_on_init

_ACCOUNT_ZERO = "rrrrrrrrrrrrrrrrrrrrrhoLvTp"  # base58 encoding of the value `0`


@require_kwargs_on_init
@dataclass(frozen=True)
class PseudoTransaction(Transaction):
    """
    Pseudo-transactions are never submitted by users, nor propagated through the
    network. Instead, a server may choose to inject pseudo-transactions in a proposed
    ledger directly according to specific protocol rules. If enough servers inject an
    identical pseudo-transaction for it to be approved by the consensus process, then
    the pseudo-transaction becomes included in the ledger, and appears in ledger data
    thereafter.
    """

    #: All pseudo-transactions have an account value of the base58 encoding of the
    #: value `0`.
    account: str = field(default=_ACCOUNT_ZERO, init=False)

    #: All pseudo-transactions have a fee value of 0.
    fee: str = field(default="0", init=False)

    #: All pseudo-transactions have a sequence value of 0.
    sequence: int = field(default=0, init=False)

    #: All pseudo-transactions have an empty signing_pub_key.
    signing_pub_key: str = field(default="", init=False)

    #: All pseudo-transactions have an empty txn_signature.
    txn_signature: str = field(default="", init=False)

    #: All pseudo-transactions do not have an empty source_tag.
    source_tag: None = field(default=None, init=False)

    transaction_type: PseudoTransactionType = REQUIRED  # type: ignore
