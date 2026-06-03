from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import LoanPay, LoanPayFlag

_SOURCE = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_LOAN_ID = "78381E3BA82D0464D27B6E7D968657EB8EFF95625A4FE623840127F61F468D4C"


class TestLoanPay(TestCase):
    def test_invalid_multiple_flags_enabled(self):
        with self.assertRaises(XRPLModelException) as error:
            LoanPay(
                account=_SOURCE,
                loan_id=_LOAN_ID,
                amount="1000",
                flags=LoanPayFlag.TF_LOAN_OVERPAYMENT
                | LoanPayFlag.TF_LOAN_FULL_PAYMENT,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'LoanPay:Flags': 'Only one flag must be enabled in the LoanPay "
            + "transaction'}",
        )

    def test_invalid_flag_input(self):
        with self.assertRaises(XRPLModelException) as error:
            LoanPay(
                account=_SOURCE,
                loan_id=_LOAN_ID,
                amount="1000",
                flags=0x00080000,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'LoanPay:Flags': 'Unrecognised flag in the LoanPay " + "transaction'}",
        )

    def test_valid_loan_pay(self):
        tx = LoanPay(
            account=_SOURCE,
            loan_id=_LOAN_ID,
            amount="1000",
        )
        self.assertTrue(tx.is_valid())
