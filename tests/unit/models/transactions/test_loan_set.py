from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import LoanSet

_SOURCE = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_ISSUER = "rHxTJLqdVUxjJuZEZvajXYYQJ7q8p4DhHy"


class TestLoanSet(TestCase):
    def test_invalid_data_too_long(self):
        with self.assertRaises(XRPLModelException) as error:
            LoanSet(
                account=_SOURCE,
                loan_broker_id=_ISSUER,
                principal_requested="100000000",
                data="A" * 257 * 2,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'LoanSet:data': 'Data must be less than 256 bytes.'}",
        )

    def test_invalid_data_non_hex_string(self):
        with self.assertRaises(XRPLModelException) as error:
            LoanSet(
                account=_SOURCE,
                loan_broker_id=_ISSUER,
                principal_requested="100000000",
                data="Z",
            )
        self.assertEqual(
            error.exception.args[0],
            "{'LoanSet:data': 'Data must be a valid hex string.'}",
        )

    def test_invalid_overpayment_fee_too_low(self):
        with self.assertRaises(XRPLModelException) as error:
            LoanSet(
                account=_SOURCE,
                loan_broker_id=_ISSUER,
                principal_requested="100000000",
                overpayment_fee=-1,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'LoanSet:overpayment_fee': 'Overpayment fee must be between 0 and 100000"
            + " inclusive.'}",
        )

    def test_invalid_interest_rate_too_low(self):
        with self.assertRaises(XRPLModelException) as error:
            LoanSet(
                account=_SOURCE,
                loan_broker_id=_ISSUER,
                principal_requested="100000000",
                interest_rate=-1,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'LoanSet:interest_rate': 'Interest rate must be between 0 and 100000"
            + " inclusive.'}",
        )

    def test_invalid_interest_rate_too_high(self):
        with self.assertRaises(XRPLModelException) as error:
            LoanSet(
                account=_SOURCE,
                loan_broker_id=_ISSUER,
                principal_requested="100000000",
                interest_rate=100001,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'LoanSet:interest_rate': 'Interest rate must be between 0 and 100000"
            + " inclusive.'}",
        )

    def test_invalid_late_interest_rate_too_low(self):
        with self.assertRaises(XRPLModelException) as error:
            LoanSet(
                account=_SOURCE,
                loan_broker_id=_ISSUER,
                principal_requested="100000000",
                late_interest_rate=-1,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'LoanSet:late_interest_rate': 'Late interest rate must be between 0 and"
            + " 100000 inclusive.'}",
        )

    def test_invalid_late_interest_rate_too_high(self):
        with self.assertRaises(XRPLModelException) as error:
            LoanSet(
                account=_SOURCE,
                loan_broker_id=_ISSUER,
                principal_requested="100000000",
                late_interest_rate=100001,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'LoanSet:late_interest_rate': 'Late interest rate must be between 0 and"
            + " 100000 inclusive.'}",
        )

    def test_invalid_close_interest_rate_too_low(self):
        with self.assertRaises(XRPLModelException) as error:
            LoanSet(
                account=_SOURCE,
                loan_broker_id=_ISSUER,
                principal_requested="100000000",
                close_interest_rate=-1,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'LoanSet:close_interest_rate': 'Close interest rate must be between 0 and"
            + " 100000 inclusive.'}",
        )

    def test_invalid_close_interest_rate_too_high(self):
        with self.assertRaises(XRPLModelException) as error:
            LoanSet(
                account=_SOURCE,
                loan_broker_id=_ISSUER,
                principal_requested="100000000",
                close_interest_rate=100001,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'LoanSet:close_interest_rate': 'Close interest rate must be between 0 and"
            + " 100000 inclusive.'}",
        )

    def test_invalid_overpayment_interest_rate_too_low(self):
        with self.assertRaises(XRPLModelException) as error:
            LoanSet(
                account=_SOURCE,
                loan_broker_id=_ISSUER,
                principal_requested="100000000",
                overpayment_interest_rate=-1,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'LoanSet:overpayment_interest_rate': 'Overpayment interest rate must be"
            + " between 0 and 100000 inclusive.'}",
        )

    def test_invalid_overpayment_interest_rate_too_high(self):
        with self.assertRaises(XRPLModelException) as error:
            LoanSet(
                account=_SOURCE,
                loan_broker_id=_ISSUER,
                principal_requested="100000000",
                overpayment_interest_rate=100001,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'LoanSet:overpayment_interest_rate': 'Overpayment interest rate must be"
            + " between 0 and 100000 inclusive.'}",
        )

    def test_invalid_overpayment_fee_too_high(self):
        with self.assertRaises(XRPLModelException) as error:
            LoanSet(
                account=_SOURCE,
                loan_broker_id=_ISSUER,
                principal_requested="100000000",
                overpayment_fee=100001,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'LoanSet:overpayment_fee': 'Overpayment fee must be between 0 and 100000"
            + " inclusive.'}",
        )

    def test_invalid_payment_interval_shorter_than_grace_period(self):
        with self.assertRaises(XRPLModelException) as error:
            LoanSet(
                account=_SOURCE,
                loan_broker_id=_ISSUER,
                principal_requested="100000000",
                payment_interval=65,
                grace_period=70,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'LoanSet:GracePeriod': 'Grace period must be less than the payment "
            + "interval.'}",
        )

    def test_invalid_payment_interval_too_short(self):
        with self.assertRaises(XRPLModelException) as error:
            LoanSet(
                account=_SOURCE,
                loan_broker_id=_ISSUER,
                principal_requested="100000000",
                payment_interval=59,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'LoanSet:PaymentInterval': 'Payment interval must be at least 60 seconds."
            + "'}",
        )

    def test_valid_loan_set(self):
        tx = LoanSet(
            account=_SOURCE,
            loan_broker_id=_ISSUER,
            principal_requested="100000000",
        )
        self.assertTrue(tx.is_valid())
