"""Sponsored-transaction fee threading through the synchronous wrappers (XLS-68)."""

from unittest import TestCase
from unittest.mock import AsyncMock, patch

from xrpl.models.transactions import Payment
from xrpl.transaction.main import autofill

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_DESTINATION = "ra5nK24KXen9AHvsdFTKHSANinZseWnPcX"
_SPONSOR = "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn"


class TestSponsorFeeSyncAutofill(TestCase):
    """The sync `autofill` wrapper must thread the new argument in the right slot.

    Not an ``IsolatedAsyncioTestCase``: the wrapper calls ``asyncio.run``, which
    cannot be invoked from inside a running event loop.
    """

    def test_sync_autofill_passes_sponsor_count_not_signers_count(self):
        """The wrapper threads positionally, so argument order matters.

        ``main.autofill(transaction, client, signers_count, sponsor_signers_count)``
        -- transposing the last two yields identical arithmetic whenever only one
        is set, so only an argument-level assertion catches it.
        """
        tx = Payment(
            account=_ACCOUNT,
            destination=_DESTINATION,
            amount="1000",
            sequence=1,
            sponsor=_SPONSOR,
            sponsor_flags=1,
        )
        with patch(
            "xrpl.asyncio.transaction.main.autofill",
            new=AsyncMock(return_value=tx),
        ) as mocked:
            autofill(tx, None, sponsor_signers_count=3)

        self.assertEqual(mocked.await_args.args[2], None)  # signers_count
        self.assertEqual(mocked.await_args.args[3], 3)  # sponsor_signers_count
