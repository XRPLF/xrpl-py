"""General XRPL Transaction Exceptions."""
from __future__ import annotations

from xrpl import XRPLException


class XRPLRequestFailureException(XRPLException):
    """XRPL Transaction Exception, when the transaction fails."""

    def __init__(
        self: XRPLRequestFailureException,
        error_code: str,
        error_message: str,
    ) -> None:
        """
        Initializes a XRPLRequestFailureException.

        Args:
            error_code: an XRPL error code (usually starts with `te`).
            error_message: the more human-readable version of the error code returned
                by the ledger.
        """
        self.error_code = error_code
        self.message = f"Transaction failed, {error_code}: {error_message}"
