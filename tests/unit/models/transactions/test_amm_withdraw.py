from unittest import TestCase

from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import AMMWithdraw
from xrpl.models.transactions.amm_withdraw import AMMWithdrawFlag

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_ASSET = {"currency": "XRP"}
_ASSET2 = {"currency": "ETH", "issuer": "rpGtkFRXhgVaBzC5XCR7gyE2AZN5SN3SEW"}
_AMOUNT = "1000"
_LPTOKEN_CURRENCY = "B3813FCAB4EE68B3D0D735D6849465A9113EE048"
_LPTOKEN_ISSUER = "rH438jEAzTs5PYtV6CHZqpDpwCKQmPW9Cg"


class TestAMMWithdraw(TestCase):
    def test_tx_valid_lptoken(self):
        tx = AMMWithdraw(
            account=_ACCOUNT,
            sequence=1337,
            asset=_ASSET,
            asset2=_ASSET2,
            lp_token=IssuedCurrencyAmount(
                currency=_LPTOKEN_CURRENCY,
                issuer=_LPTOKEN_ISSUER,
                value=_AMOUNT,
            ),
            flags=AMMWithdrawFlag.TF_LP_TOKEN,
        )
        self.assertTrue(tx.is_valid())

    def test_tx_valid_amount(self):
        tx = AMMWithdraw(
            account=_ACCOUNT,
            sequence=1337,
            asset=_ASSET,
            asset2=_ASSET2,
            amount=_AMOUNT,
            flags=AMMWithdrawFlag.TF_SINGLE_ASSET,
        )
        self.assertTrue(tx.is_valid())

    def test_tx_valid_amount_amount2(self):
        tx = AMMWithdraw(
            account=_ACCOUNT,
            sequence=1337,
            asset=_ASSET,
            asset2=_ASSET2,
            amount=_AMOUNT,
            amount2="500",
            flags=AMMWithdrawFlag.TF_TWO_ASSET,
        )
        self.assertTrue(tx.is_valid())

    def test_tx_valid_amount_lptoken(self):
        tx = AMMWithdraw(
            account=_ACCOUNT,
            sequence=1337,
            asset=_ASSET,
            asset2=_ASSET2,
            amount=_AMOUNT,
            lp_token=IssuedCurrencyAmount(
                currency=_LPTOKEN_CURRENCY,
                issuer=_LPTOKEN_ISSUER,
                value="500",
            ),
            flags=AMMWithdrawFlag.TF_ONE_ASSET_LP_TOKEN,
        )
        self.assertTrue(tx.is_valid())

    def test_tx_valid_amount_eprice(self):
        tx = AMMWithdraw(
            account=_ACCOUNT,
            sequence=1337,
            asset=_ASSET,
            asset2=_ASSET2,
            amount=_AMOUNT,
            e_price="25",
            flags=AMMWithdrawFlag.TF_LIMIT_LP_TOKEN,
        )
        self.assertTrue(tx.is_valid())

    def test_undefined_amount_undefined_lptoken_invalid_combo(self):
        with self.assertRaises(XRPLModelException) as error:
            AMMWithdraw(
                account=_ACCOUNT,
                sequence=1337,
                asset=_ASSET,
                asset2=_ASSET2,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'AMMWithdraw': 'Must set at least `lp_token` or `amount`'}",
        )

    def test_undefined_amount_defined_amount2_invalid_combo(self):
        with self.assertRaises(XRPLModelException) as error:
            AMMWithdraw(
                account=_ACCOUNT,
                sequence=1337,
                asset=_ASSET,
                asset2=_ASSET2,
                amount2="500",
            )
        self.assertEqual(
            error.exception.args[0],
            "{'AMMWithdraw': 'Must set `amount` with `amount2`'}",
        )

    def test_undefined_amount_defined_eprice_invalid_combo(self):
        with self.assertRaises(XRPLModelException) as error:
            AMMWithdraw(
                account=_ACCOUNT,
                sequence=1337,
                asset=_ASSET,
                asset2=_ASSET2,
                e_price="25",
            )
        self.assertEqual(
            error.exception.args[0],
            "{'AMMWithdraw': 'Must set `amount` with `e_price`'}",
        )
