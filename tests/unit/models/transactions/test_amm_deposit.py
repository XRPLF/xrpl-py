from unittest import TestCase

from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import AMMDeposit

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_AMM_ID = "24BA86F99302CF124AB27311C831F5BFAA72C4625DDA65B7EDF346A60CC19883"
_AMOUNT = "1000"
_LPTOKEN_CURRENCY = "B3813FCAB4EE68B3D0D735D6849465A9113EE048"
_LPTOKEN_ISSUER = "rH438jEAzTs5PYtV6CHZqpDpwCKQmPW9Cg"


class TestAMMDeposit(TestCase):
    def test_tx_valid_xrpl_lptoken(self):
        tx = AMMDeposit(
            account=_ACCOUNT,
            sequence=1337,
            amm_id=_AMM_ID,
            lp_token=IssuedCurrencyAmount(
                currency=_LPTOKEN_CURRENCY,
                issuer=_LPTOKEN_ISSUER,
                value=_AMOUNT,
            ),
        )
        self.assertTrue(tx.is_valid())

    def test_tx_valid_asset1in(self):
        tx = AMMDeposit(
            account=_ACCOUNT,
            sequence=1337,
            amm_id=_AMM_ID,
            asset1_in=_AMOUNT,
        )
        self.assertTrue(tx.is_valid())

    def test_tx_valid_asset1in_asset2in(self):
        tx = AMMDeposit(
            account=_ACCOUNT,
            sequence=1337,
            amm_id=_AMM_ID,
            asset1_in=_AMOUNT,
            asset2_in="500",
        )
        self.assertTrue(tx.is_valid())

    def test_tx_valid_asset1in_lptoken(self):
        tx = AMMDeposit(
            account=_ACCOUNT,
            sequence=1337,
            amm_id=_AMM_ID,
            asset1_in=_AMOUNT,
            lp_token=IssuedCurrencyAmount(
                currency=_LPTOKEN_CURRENCY,
                issuer=_LPTOKEN_ISSUER,
                value="500",
            ),
        )
        self.assertTrue(tx.is_valid())

    def test_tx_valid_asset1in_eprice(self):
        tx = AMMDeposit(
            account=_ACCOUNT,
            sequence=1337,
            amm_id=_AMM_ID,
            asset1_in=_AMOUNT,
            e_price="25",
        )
        self.assertTrue(tx.is_valid())

    def test_undefined_asset1in_undefined_lptoken_invalid_combo(self):
        with self.assertRaises(XRPLModelException) as error:
            AMMDeposit(
                account=_ACCOUNT,
                sequence=1337,
                amm_id=_AMM_ID,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'AMMDeposit': 'Must set at least `lp_token` or `asset1_in`'}",
        )

    def test_undefined_asset1in_defined_asset2in_invalid_combo(self):
        with self.assertRaises(XRPLModelException) as error:
            AMMDeposit(
                account=_ACCOUNT,
                sequence=1337,
                amm_id=_AMM_ID,
                asset2_in="500",
            )
        self.assertEqual(
            error.exception.args[0],
            "{'AMMDeposit': 'Must set `asset1_in` with `asset2_in`'}",
        )

    def test_undefined_asset1in_defined_eprice_invalid_combo(self):
        with self.assertRaises(XRPLModelException) as error:
            AMMDeposit(
                account=_ACCOUNT,
                sequence=1337,
                amm_id=_AMM_ID,
                e_price="25",
            )
        self.assertEqual(
            error.exception.args[0],
            "{'AMMDeposit': 'Must set `asset1_in` with `e_price`'}",
        )
