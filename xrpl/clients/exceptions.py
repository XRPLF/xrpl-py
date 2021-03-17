"""General XRPL Transaction Exceptions."""
from __future__ import annotations

from xrpl import XRPLException


class XRPLTransactionFailureException(XRPLException):
    """XRPL Transaction Exception, when the transaction fails."""

    def __init__(
        self: XRPLTransactionFailureException,
        error_code: str,
        error_message: str,
    ) -> None:
        """
        Initializes a XRPLTransactionFailureException.

        Args:
            error_code: an XRPL error code (usually starts with `te`).
            error_message: the more human-readable version of the error code returned
                by the ledger.
        """
        self.error_code = error_code
        self.message = f"Transaction failed, {error_code}: {error_message}"
