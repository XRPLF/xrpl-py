"""
Represents a SetRegularKey transaction on the XRP Ledger.

A SetRegularKey transaction assigns, changes, or removes the regular key pair
associated with an account. You can protect your account by assigning a regular key
pair to it and using it instead of the master key pair to sign transactions whenever
possible. If your regular key pair is compromised, but your master key pair is not, you
can use a SetRegularKey transaction to regain control of your account.

`See SetRegularKey <https://xrpl.org/setregularkey.html>`_
"""
from __future__ import annotations  # Requires Python 3.7+

from typing import Any, List, Optional

from xrpl.models.transactions.transaction import Transaction, TransactionType


class SetRegularKeyTransaction(Transaction):
    """
    Represents a SetRegularKey transaction on the XRP Ledger.

    A SetRegularKey transaction assigns, changes, or removes the regular key pair
    associated with an account.You can protect your account by assigning a regular key
    pair to it and using it instead of the master key pair to sign transactions
    whenever possible. If your regular key pair is compromised, but your master key
    pair is not, you can use a SetRegularKey transaction to regain control of your
    account.

    `See SetRegularKey <https://xrpl.org/setregularkey.html>`_
    """

    def __init__(
        self: SetRegularKeyTransaction,
        *,  # forces remaining params to be named, not just listed
        account: str,
        fee: str,
        sequence: int,
        regular_key: Optional[str] = None,
        account_transaction_id: Optional[str] = None,
        flags: Optional[int] = None,
        last_ledger_sequence: Optional[int] = None,
        memos: Optional[List[Any]] = None,
        signers: Optional[List[Any]] = None,
        source_tag: Optional[int] = None,
        signing_public_key: Optional[str] = None,
        transaction_signature: Optional[str] = None,
    ) -> None:
        """Construct a SetRegularKeyTransaction from the given parameters."""
        self.regular_key = regular_key

        super().__init__(
            account=account,
            transaction_type=TransactionType.SetRegularKey,
            fee=fee,
            sequence=sequence,
            account_transaction_id=account_transaction_id,
            flags=flags,
            last_ledger_sequence=last_ledger_sequence,
            memos=memos,
            signers=signers,
            source_tag=source_tag,
            signing_public_key=signing_public_key,
            transaction_signature=transaction_signature,
        )
