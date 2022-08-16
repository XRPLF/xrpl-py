from unittest import TestCase

from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import AMMWithdraw

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_AMM_ID = "24BA86F99302CF124AB27311C831F5BFAA72C4625DDA65B7EDF346A60CC19883"
_AMOUNT = "1000"
_LPTOKEN_CURRENCY = "B3813FCAB4EE68B3D0D735D6849465A9113EE048"
_LPTOKEN_ISSUER = "rH438jEAzTs5PYtV6CHZqpDpwCKQmPW9Cg"


class TestAMMWithdraw(TestCase):
    def test_to_xrpl_lptokens(self):
        tx = AMMWithdraw(
            account=_ACCOUNT,
            sequence=1337,
            amm_id=_AMM_ID,
            lptokens=IssuedCurrencyAmount(
                currency=_LPTOKEN_CURRENCY,
                issuer=_LPTOKEN_ISSUER,
                value=_AMOUNT,
            ),
        )
        expected = {
            "AMMID": _AMM_ID,
            "Account": "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ",
            "LPTokens": {
                "currency": "B3813FCAB4EE68B3D0D735D6849465A9113EE048",
                "issuer": "rH438jEAzTs5PYtV6CHZqpDpwCKQmPW9Cg",
                "value": "1000",
            },
            "TransactionType": "AMMWithdraw",
            "Sequence": 1337,
            "SigningPubKey": "",
            "Flags": 0,
        }
        self.assertEqual(tx.to_xrpl(), expected)

    def test_to_xrpl_asset1out(self):
        tx = AMMWithdraw(
            account=_ACCOUNT,
            sequence=1337,
            amm_id=_AMM_ID,
            asset1_out=_AMOUNT,
        )
        expected = {
            "AMMID": _AMM_ID,
            "Account": "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ",
            "Asset1Out": "1000",
            "TransactionType": "AMMWithdraw",
            "Sequence": 1337,
            "SigningPubKey": "",
            "Flags": 0,
        }
        self.assertEqual(tx.to_xrpl(), expected)

    def test_to_xrpl_asset1out_asset2out(self):
        tx = AMMWithdraw(
            account=_ACCOUNT,
            sequence=1337,
            amm_id=_AMM_ID,
            asset1_out=_AMOUNT,
            asset2_out="500",
        )
        expected = {
            "AMMID": _AMM_ID,
            "Account": "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ",
            "Asset1Out": "1000",
            "Asset2Out": "500",
            "TransactionType": "AMMWithdraw",
            "Sequence": 1337,
            "SigningPubKey": "",
            "Flags": 0,
        }
        self.assertEqual(tx.to_xrpl(), expected)

    def test_to_xrpl_asset1out_lptokens(self):
        tx = AMMWithdraw(
            account=_ACCOUNT,
            sequence=1337,
            amm_id=_AMM_ID,
            asset1_out=_AMOUNT,
            lptokens=IssuedCurrencyAmount(
                currency=_LPTOKEN_CURRENCY,
                issuer=_LPTOKEN_ISSUER,
                value="500",
            ),
        )
        expected = {
            "AMMID": _AMM_ID,
            "Account": "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ",
            "Asset1Out": "1000",
            "LPTokens": {
                "currency": "B3813FCAB4EE68B3D0D735D6849465A9113EE048",
                "issuer": "rH438jEAzTs5PYtV6CHZqpDpwCKQmPW9Cg",
                "value": "500",
            },
            "TransactionType": "AMMWithdraw",
            "Sequence": 1337,
            "SigningPubKey": "",
            "Flags": 0,
        }
        self.assertEqual(tx.to_xrpl(), expected)

    def test_to_xrpl_asset1out_eprice(self):
        tx = AMMWithdraw(
            account=_ACCOUNT,
            sequence=1337,
            amm_id=_AMM_ID,
            asset1_out=_AMOUNT,
            e_price="25",
        )
        expected = {
            "AMMID": _AMM_ID,
            "Account": "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ",
            "Asset1Out": "1000",
            "EPrice": "25",
            "TransactionType": "AMMWithdraw",
            "Sequence": 1337,
            "SigningPubKey": "",
            "Flags": 0,
        }
        self.assertEqual(tx.to_xrpl(), expected)

    def test_undefined_asset1out_undefined_lptokens_invalid_combo(self):
        with self.assertRaises(XRPLModelException):
            AMMWithdraw(
                account=_ACCOUNT,
                sequence=1337,
                amm_id=_AMM_ID,
            )

    def test_undefined_asset1out_defined_asset2out_invalid_combo(self):
        with self.assertRaises(XRPLModelException):
            AMMWithdraw(
                account=_ACCOUNT,
                sequence=1337,
                amm_id=_AMM_ID,
                asset2_out="500",
            )

    def test_undefined_asset1out_defined_eprice_invalid_combo(self):
        with self.assertRaises(XRPLModelException):
            AMMWithdraw(
                account=_ACCOUNT,
                sequence=1337,
                amm_id=_AMM_ID,
                e_price="25",
            )
