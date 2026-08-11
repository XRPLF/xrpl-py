"""Unit tests for the reliable-submission helpers.

Covers the control flow of ``submit_and_wait`` and ``_get_signed_tx`` -- blob
decoding, the already-signed short-circuit, the missing-wallet guard, the
fee-check and autofill toggles, and single- vs multi-sign selection -- with the
network and signing sinks stubbed. Fee arithmetic and the sponsor/signer count
threading are covered separately in ``test_sponsor_fee.py``.
"""

from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, Mock, patch

from xrpl.asyncio.transaction.reliable_submission import (
    _get_signed_tx,
    submit_and_wait,
)
from xrpl.constants import XRPLException

_MODULE = "xrpl.asyncio.transaction.reliable_submission"


def _tx(*, signed: bool = False, signers=None) -> Mock:
    """A stand-in transaction with controllable is_signed()/signers."""
    tx = Mock()
    tx.is_signed.return_value = signed
    tx.signers = signers
    return tx


class TestGetSignedTx(IsolatedAsyncioTestCase):
    async def test_string_blob_is_decoded(self):
        """A blob string is turned into a Transaction before anything else."""
        decoded = _tx(signed=True)  # signed, so it returns right after decoding
        with patch(f"{_MODULE}.Transaction") as transaction_cls:
            transaction_cls.from_blob.return_value = decoded
            result = await _get_signed_tx("DEADBEEF", None)

        transaction_cls.from_blob.assert_called_once_with("DEADBEEF")
        self.assertIs(result, decoded)

    async def test_already_signed_is_returned_untouched(self):
        """A signed transaction skips fee-check, autofill, and re-signing."""
        signed = _tx(signed=True)
        with (
            patch(f"{_MODULE}._check_fee", new=AsyncMock()) as check_fee,
            patch(f"{_MODULE}._autofill", new=AsyncMock()) as autofill,
            patch(f"{_MODULE}.sign", new=Mock()) as sign,
        ):
            result = await _get_signed_tx(signed, None, Mock())

        self.assertIs(result, signed)
        check_fee.assert_not_called()
        autofill.assert_not_called()
        sign.assert_not_called()

    async def test_unsigned_without_wallet_raises(self):
        """An unsigned transaction cannot be signed without a wallet."""
        with self.assertRaises(XRPLException):
            await _get_signed_tx(_tx(signed=False), None, wallet=None)

    async def test_unsigned_single_signs_when_no_signers(self):
        """No pre-existing Signers -> single-signature signing."""
        tx = _tx(signed=False, signers=None)
        with (
            patch(f"{_MODULE}._check_fee", new=AsyncMock()) as check_fee,
            patch(
                f"{_MODULE}._autofill",
                new=AsyncMock(side_effect=lambda t, *a, **k: t),
            ) as autofill,
            patch(
                f"{_MODULE}.sign", new=Mock(side_effect=lambda t, *a, **k: t)
            ) as sign,
        ):
            await _get_signed_tx(tx, None, Mock())

        check_fee.assert_awaited_once()
        autofill.assert_awaited_once()
        self.assertIs(sign.call_args.kwargs.get("multisign"), False)

    async def test_unsigned_multi_signs_when_signers_present(self):
        """Pre-existing Signers -> multi-signature signing."""
        tx = _tx(signed=False, signers=[Mock()])
        with (
            patch(f"{_MODULE}._check_fee", new=AsyncMock()),
            patch(
                f"{_MODULE}._autofill",
                new=AsyncMock(side_effect=lambda t, *a, **k: t),
            ),
            patch(
                f"{_MODULE}.sign", new=Mock(side_effect=lambda t, *a, **k: t)
            ) as sign,
        ):
            await _get_signed_tx(tx, None, Mock())

        self.assertIs(sign.call_args.kwargs.get("multisign"), True)

    async def test_toggles_skip_fee_check_and_autofill(self):
        """check_fee=False and autofill=False bypass both steps."""
        tx = _tx(signed=False, signers=None)
        with (
            patch(f"{_MODULE}._check_fee", new=AsyncMock()) as check_fee,
            patch(f"{_MODULE}._autofill", new=AsyncMock()) as autofill,
            patch(f"{_MODULE}.sign", new=Mock(side_effect=lambda t, *a, **k: t)),
        ):
            await _get_signed_tx(tx, None, Mock(), check_fee=False, autofill=False)

        check_fee.assert_not_called()
        autofill.assert_not_called()


class TestSubmitAndWait(IsolatedAsyncioTestCase):
    async def test_delegates_to_get_signed_tx_then_sends(self):
        """submit_and_wait signs via _get_signed_tx, then reliably submits."""
        signed = Mock()
        response = Mock()
        with (
            patch(
                f"{_MODULE}._get_signed_tx", new=AsyncMock(return_value=signed)
            ) as get_signed,
            patch(
                f"{_MODULE}._send_reliable_submission",
                new=AsyncMock(return_value=response),
            ) as send,
        ):
            result = await submit_and_wait(Mock(), None, Mock(), fail_hard=True)

        get_signed.assert_awaited_once()
        send.assert_awaited_once_with(signed, None, fail_hard=True)
        self.assertIs(result, response)

    async def test_forwards_sponsor_signers_count(self):
        """The sponsor count must reach the fee layer via _get_signed_tx."""
        with (
            patch(f"{_MODULE}._check_fee", new=AsyncMock()) as check_fee,
            patch(
                f"{_MODULE}._autofill",
                new=AsyncMock(side_effect=lambda t, *a, **k: t),
            ) as autofill,
            patch(f"{_MODULE}.sign", new=Mock(side_effect=lambda t, *a, **k: t)),
            patch(f"{_MODULE}._send_reliable_submission", new=AsyncMock()),
        ):
            await submit_and_wait(
                _tx(signed=False), None, Mock(), sponsor_signers_count=3
            )

        self.assertEqual(check_fee.await_args.kwargs["sponsor_signers_count"], 3)
        self.assertEqual(autofill.await_args.kwargs["sponsor_signers_count"], 3)

    async def test_forwards_signers_count(self):
        """The multisign path bills the sponsee's own signers via signers_count."""
        with (
            patch(f"{_MODULE}._check_fee", new=AsyncMock()) as check_fee,
            patch(
                f"{_MODULE}._autofill",
                new=AsyncMock(side_effect=lambda t, *a, **k: t),
            ) as autofill,
            patch(f"{_MODULE}.sign", new=Mock(side_effect=lambda t, *a, **k: t)),
            patch(f"{_MODULE}._send_reliable_submission", new=AsyncMock()),
        ):
            await submit_and_wait(_tx(signed=False), None, Mock(), signers_count=2)

        self.assertEqual(check_fee.await_args.kwargs["signers_count"], 2)
        self.assertEqual(autofill.await_args.kwargs["signers_count"], 2)
