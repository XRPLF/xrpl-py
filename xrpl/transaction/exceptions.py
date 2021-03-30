"""General XRPL Transaction Exceptions."""

from __future__ import annotations

from xrpl.constants import XRPLException


class XRPLReliableSubmissionException(XRPLException):
    """General XRPL Reliable Submission Exception."""

    pass


class LastLedgerSequenceExpiredException(XRPLReliableSubmissionException):
    """
    XRPL Reliable Submission Exception, when the latest ledger sequence exceeds the
    last ledger sequence in a transaction.
    """

    def __init__(
        self: LastLedgerSequenceExpiredException,
        last_ledger_sequence: int,
        latest_ledger_sequence: int,
    ) -> None:
        """
        Initializes a LastLedgerSequenceExpiredException.

        Args:
            last_ledger_sequence: the transaction's last ledger sequence.
            latest_ledger_sequence: the latest sequence value in the ledger.
        """
        self.message = (
            f"The latest ledger sequence {latest_ledger_sequence} is greater than the "
            f"last ledger sequence {last_ledger_sequence} in the transaction."
        )
