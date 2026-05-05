from unittest import TestCase

from xrpl.constants import MPT_ISSUANCE_ID_LENGTH
from xrpl.models.amounts import MPTAmount
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.check_cash import CheckCash

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_FEE = "0.00001"
_SEQUENCE = 19048
_CHECK_ID = "838766BA2B995C00744175F69A1B11E32C3DBC40E64801A4056FCBD657F57334"
_MPT_ISSUANCE_ID = "00000001A407AF5856CECE4281FED12B7B179B49A4AEF506"
_AMOUNT = "300"


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

    def test_mpt_amount_is_valid(self):
        tx = CheckCash(
            account=_ACCOUNT,
            fee=_FEE,
            sequence=_SEQUENCE,
            check_id=_CHECK_ID,
            amount=MPTAmount(
                mpt_issuance_id=_MPT_ISSUANCE_ID,
                value="50",
            ),
        )
        self.assertTrue(tx.is_valid())

    def test_mpt_amount_non_hex_characters(self):
        bad_id = "Z" * MPT_ISSUANCE_ID_LENGTH
        with self.assertRaises(XRPLModelException) as error:
            CheckCash(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                check_id=_CHECK_ID,
                amount=MPTAmount(
                    mpt_issuance_id=bad_id,
                    value="50",
                ),
            )
        self.assertEqual(
            error.exception.args[0],
            f"{{'mpt_issuance_id': 'Invalid mpt_issuance_id {bad_id}'}}",
        )

    def test_mpt_amount_id_too_short(self):
        bad_id = "A" * (MPT_ISSUANCE_ID_LENGTH - 1)
        with self.assertRaises(XRPLModelException) as error:
            CheckCash(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                check_id=_CHECK_ID,
                amount=MPTAmount(
                    mpt_issuance_id=bad_id,
                    value="50",
                ),
            )
        self.assertEqual(
            error.exception.args[0],
            f"{{'mpt_issuance_id': 'Invalid mpt_issuance_id {bad_id}'}}",
        )

    def test_mpt_amount_id_too_long(self):
        bad_id = "A" * (MPT_ISSUANCE_ID_LENGTH + 1)
        with self.assertRaises(XRPLModelException) as error:
            CheckCash(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                check_id=_CHECK_ID,
                amount=MPTAmount(
                    mpt_issuance_id=bad_id,
                    value="50",
                ),
            )
        self.assertEqual(
            error.exception.args[0],
            f"{{'mpt_issuance_id': 'Invalid mpt_issuance_id {bad_id}'}}",
        )
