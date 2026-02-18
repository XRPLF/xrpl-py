from sys import maxsize
from unittest import TestCase

from xrpl.models.amounts import IssuedCurrencyAmount, MPTAmount
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import AMMCreate

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_IOU_ISSUER = "rPyfep3gcLzkosKC9XiE77Y8DZWG6iWDT9"
_MPT_ISSUANCE_ID = "00000001A407AF5856CECE4281FED12B7B179B49A4AEF506"


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

    def test_tx_valid_with_two_mpt_assets(self):
        tx = AMMCreate(
            account=_ACCOUNT,
            amount=MPTAmount(
                mpt_issuance_id=_MPT_ISSUANCE_ID,
                value="250",
            ),
            amount2=MPTAmount(
                mpt_issuance_id="00000002A407AF5856CECE4281FED12B7B179B49A4AEF506",
                value="250",
            ),
            trading_fee=12,
        )
        self.assertTrue(tx.is_valid())

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
