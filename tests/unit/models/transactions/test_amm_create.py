from sys import maxsize
from unittest import TestCase

from xrpl.core.binarycodec import decode
from xrpl.models.amounts import IssuedCurrencyAmount, MPTAmount
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import AMMCreate

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_IOU_ISSUER = "rPyfep3gcLzkosKC9XiE77Y8DZWG6iWDT9"
_MPT_ID = "00000003430427B80BD2D09D36B70B969E12801065F22308"
_MPT_ID2 = "00000004430427B80BD2D09D36B70B969E12801065F22308"


class TestAMMCreate(TestCase):
    def test_tx_is_valid(self):
        tx = AMMCreate(
            account=_ACCOUNT,
            amount="1000",
            amount2=IssuedCurrencyAmount(
                currency="USD", issuer=_IOU_ISSUER, value="1000"
            ),
            trading_fee=12,
        )
        self.assertTrue(tx.is_valid())

    def test_trading_fee_too_high(self):
        with self.assertRaises(XRPLModelException) as error:
            AMMCreate(
                account=_ACCOUNT,
                amount="1000",
                amount2=IssuedCurrencyAmount(
                    currency="USD", issuer=_IOU_ISSUER, value="1000"
                ),
                trading_fee=maxsize,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'trading_fee': 'Must be between 0 and 1000'}",
        )

    def test_trading_fee_negative_number(self):
        with self.assertRaises(XRPLModelException) as error:
            AMMCreate(
                account=_ACCOUNT,
                amount="1000",
                amount2=IssuedCurrencyAmount(
                    currency="USD", issuer=_IOU_ISSUER, value="1000"
                ),
                trading_fee=-1,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'trading_fee': 'Must be between 0 and 1000'}",
        )

    def test_tx_is_valid_with_mpt(self):
        for amount in ("1000", MPTAmount(mpt_issuance_id=_MPT_ID2, value="1000")):
            with self.subTest(amount=amount):
                tx = AMMCreate(
                    account=_ACCOUNT,
                    amount=amount,
                    amount2=MPTAmount(mpt_issuance_id=_MPT_ID, value="1000"),
                    trading_fee=12,
                )
                self.assertTrue(tx.is_valid())
                self.assertEqual(decode(tx.blob()), tx.to_xrpl())
