from unittest import TestCase

from xrpl.core.binarycodec import decode
from xrpl.models.amounts import MPTAmount
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.check_cash import CheckCash

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_FEE = "0.00001"
_SEQUENCE = 19048
_CHECK_ID = "838766BA2B995C00744175F69A1B11E32C3DBC40E64801A4056FCBD657F57334"
_AMOUNT = "300"
_MPT_AMOUNT = MPTAmount(
    mpt_issuance_id="00000003430427B80BD2D09D36B70B969E12801065F22308", value="300"
)


class TestCheckCash(TestCase):
    def test_amount_and_deliver_min_is_invalid(self):
        with self.assertRaises(XRPLModelException):
            CheckCash(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                check_id=_CHECK_ID,
                amount=_AMOUNT,
                deliver_min=_AMOUNT,
            )

    def test_neither_amount_not_deliver_min_is_invalid(self):
        with self.assertRaises(XRPLModelException):
            CheckCash(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                check_id=_CHECK_ID,
            )

    def test_amount_without_deliver_min_is_valid(self):
        tx = CheckCash(
            account=_ACCOUNT,
            fee=_FEE,
            sequence=_SEQUENCE,
            check_id=_CHECK_ID,
            amount=_AMOUNT,
        )
        self.assertTrue(tx.is_valid())

    def test_deliver_min_without_amount_is_valid(self):
        tx = CheckCash(
            account=_ACCOUNT,
            fee=_FEE,
            sequence=_SEQUENCE,
            check_id=_CHECK_ID,
            deliver_min=_AMOUNT,
        )
        self.assertTrue(tx.is_valid())

    def test_mpt_amount_or_deliver_min_is_valid(self):
        for field in ("amount", "deliver_min"):
            with self.subTest(field=field):
                tx = CheckCash(
                    account=_ACCOUNT,
                    check_id=_CHECK_ID,
                    **{field: _MPT_AMOUNT},
                )
                self.assertTrue(tx.is_valid())
                self.assertEqual(decode(tx.blob()), tx.to_xrpl())
