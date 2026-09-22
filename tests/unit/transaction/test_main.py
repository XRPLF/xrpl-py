"""Delegation of the synchronous transaction wrappers to the async layer.

The sync ``sign_and_submit`` / ``autofill_and_sign`` / ``autofill`` wrappers
thread their arguments *positionally* into ``asyncio.run(main.<fn>(...))``, so a
transposition would type-check and often compute identically -- only an
argument-order assertion catches it. Behavior itself is covered by the async
``test_main.py``.

(``submit_and_wait`` threads by keyword, so it carries no such risk and is not
retested here.)
"""

from unittest import TestCase
from unittest.mock import AsyncMock, Mock, patch

from xrpl.transaction.main import autofill, autofill_and_sign, sign_and_submit


class TestSyncSignAndSubmit(TestCase):
    def test_delegates_positionally_to_async(self):
        """(transaction, client, wallet, autofill, check_fee, sponsor_signers_count)."""
        tx, client, wallet = Mock(), Mock(), Mock()
        with patch(
            "xrpl.asyncio.transaction.main.sign_and_submit", new=AsyncMock()
        ) as mocked:
            sign_and_submit(tx, client, wallet, sponsor_signers_count=3)

        args = mocked.await_args.args
        self.assertIs(args[0], tx)
        self.assertIs(args[1], client)
        self.assertIs(args[2], wallet)
        self.assertEqual(args[3], True)  # autofill default
        self.assertEqual(args[4], True)  # check_fee default
        self.assertEqual(args[5], 3)  # sponsor_signers_count


class TestSyncAutofillAndSign(TestCase):
    def test_delegates_positionally_to_async(self):
        """(transaction, client, wallet, check_fee, sponsor_signers_count)."""
        tx, client, wallet = Mock(), Mock(), Mock()
        with patch(
            "xrpl.asyncio.transaction.main.autofill_and_sign", new=AsyncMock()
        ) as mocked:
            autofill_and_sign(tx, client, wallet, sponsor_signers_count=3)

        args = mocked.await_args.args
        self.assertIs(args[0], tx)
        self.assertIs(args[1], client)
        self.assertIs(args[2], wallet)
        self.assertEqual(args[3], True)  # check_fee default
        self.assertEqual(args[4], 3)  # sponsor_signers_count


class TestSyncAutofill(TestCase):
    def test_delegates_positionally_to_async(self):
        """(transaction, client, signers_count, sponsor_signers_count).

        Transposing the last two yields identical arithmetic whenever only one
        is set, so only an argument-order assertion catches it.
        """
        tx, client = Mock(), Mock()
        with patch(
            "xrpl.asyncio.transaction.main.autofill",
            new=AsyncMock(return_value=tx),
        ) as mocked:
            autofill(tx, client, sponsor_signers_count=3)

        args = mocked.await_args.args
        self.assertIs(args[0], tx)
        self.assertIs(args[1], client)
        self.assertEqual(args[2], None)  # signers_count
        self.assertEqual(args[3], 3)  # sponsor_signers_count
