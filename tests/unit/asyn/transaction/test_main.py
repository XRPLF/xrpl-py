"""Unit tests for the transaction convenience entry points.

Covers the control flow of ``sign_and_submit`` and ``autofill_and_sign`` -- the
autofill vs. manual paths and the fee-check toggle -- with the fee, sign, and
submit sinks stubbed. Fee arithmetic and the sponsor/signer count threading are
covered separately in ``test_sponsor_fee.py``.
"""

from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, Mock, patch

from xrpl.asyncio.transaction.main import autofill_and_sign, sign_and_submit

_MODULE = "xrpl.asyncio.transaction.main"


class TestSignAndSubmit(IsolatedAsyncioTestCase):
    async def test_autofill_path_delegates_then_submits(self):
        """autofill=True routes through autofill_and_sign, then submits."""
        signed = Mock()
        response = Mock()
        with (
            patch(
                f"{_MODULE}.autofill_and_sign", new=AsyncMock(return_value=signed)
            ) as autofill_and_sign_mock,
            patch(f"{_MODULE}.submit", new=AsyncMock(return_value=response)) as submit,
        ):
            result = await sign_and_submit(Mock(), None, Mock())

        autofill_and_sign_mock.assert_awaited_once()
        submit.assert_awaited_once_with(signed, None)
        self.assertIs(result, response)

    async def test_manual_path_checks_fee_signs_and_submits(self):
        """autofill=False checks the fee, signs locally, then submits."""
        signed = Mock()
        with (
            patch(f"{_MODULE}._check_fee", new=AsyncMock()) as check_fee,
            patch(f"{_MODULE}.sign", new=Mock(return_value=signed)) as sign,
            patch(f"{_MODULE}.submit", new=AsyncMock()) as submit,
        ):
            await sign_and_submit(Mock(), None, Mock(), autofill=False)

        check_fee.assert_awaited_once()
        sign.assert_called_once()
        submit.assert_awaited_once_with(signed, None)

    async def test_manual_path_skips_fee_check_when_disabled(self):
        """autofill=False, check_fee=False signs and submits without a fee check."""
        with (
            patch(f"{_MODULE}._check_fee", new=AsyncMock()) as check_fee,
            patch(f"{_MODULE}.sign", new=Mock()),
            patch(f"{_MODULE}.submit", new=AsyncMock()) as submit,
        ):
            await sign_and_submit(Mock(), None, Mock(), autofill=False, check_fee=False)

        check_fee.assert_not_called()
        submit.assert_awaited_once()

    async def test_forwards_sponsor_signers_count(self):
        """The sponsor count must reach the fee layer, not stop at the entry point."""
        with (
            patch(f"{_MODULE}._check_fee", new=AsyncMock()) as check_fee,
            patch(
                f"{_MODULE}.autofill",
                new=AsyncMock(side_effect=lambda tx, *a, **k: tx),
            ) as autofill,
            patch(f"{_MODULE}.sign", new=Mock(side_effect=lambda tx, *a, **k: tx)),
            patch(f"{_MODULE}.submit", new=AsyncMock()),
        ):
            await sign_and_submit(Mock(), None, Mock(), sponsor_signers_count=3)

        self.assertEqual(check_fee.await_args.kwargs["sponsor_signers_count"], 3)
        self.assertEqual(autofill.await_args.kwargs["sponsor_signers_count"], 3)


class TestAutofillAndSign(IsolatedAsyncioTestCase):
    async def test_checks_fee_autofills_then_single_signs(self):
        """The fee is checked, the tx autofilled, then single-signed."""
        autofilled = Mock()
        signed = Mock()
        wallet = Mock()
        with (
            patch(f"{_MODULE}._check_fee", new=AsyncMock()) as check_fee,
            patch(
                f"{_MODULE}.autofill", new=AsyncMock(return_value=autofilled)
            ) as autofill,
            patch(f"{_MODULE}.sign", new=Mock(return_value=signed)) as sign,
        ):
            result = await autofill_and_sign(Mock(), None, wallet)

        check_fee.assert_awaited_once()
        autofill.assert_awaited_once()
        # Signs the *autofilled* transaction, always single-signature.
        self.assertIs(sign.call_args.args[0], autofilled)
        self.assertIs(sign.call_args.kwargs.get("multisign"), False)
        self.assertIs(result, signed)

    async def test_skips_fee_check_when_disabled(self):
        """check_fee=False autofills and signs without a fee check."""
        with (
            patch(f"{_MODULE}._check_fee", new=AsyncMock()) as check_fee,
            patch(f"{_MODULE}.autofill", new=AsyncMock(return_value=Mock())),
            patch(f"{_MODULE}.sign", new=Mock()) as sign,
        ):
            await autofill_and_sign(Mock(), None, Mock(), check_fee=False)

        check_fee.assert_not_called()
        sign.assert_called_once()

    async def test_forwards_sponsor_signers_count(self):
        """The sponsor count must reach both the fee check and autofill."""
        with (
            patch(f"{_MODULE}._check_fee", new=AsyncMock()) as check_fee,
            patch(
                f"{_MODULE}.autofill",
                new=AsyncMock(side_effect=lambda tx, *a, **k: tx),
            ) as autofill,
            patch(f"{_MODULE}.sign", new=Mock(side_effect=lambda tx, *a, **k: tx)),
        ):
            await autofill_and_sign(Mock(), None, Mock(), sponsor_signers_count=3)

        self.assertEqual(check_fee.await_args.kwargs["sponsor_signers_count"], 3)
        self.assertEqual(autofill.await_args.kwargs["sponsor_signers_count"], 3)
