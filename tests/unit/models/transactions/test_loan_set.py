import datetime
from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import LoanSet

_SOURCE = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_ISSUER = "rHxTJLqdVUxjJuZEZvajXYYQJ7q8p4DhHy"


class TestLoanSet(TestCase):
    def test_invalid_payment_interval_shorter_than_grace_period(self):
        with self.assertRaises(XRPLModelException) as error:
            LoanSet(
                account=_SOURCE,
                loan_broker_id=_ISSUER,
                principal_requested="100000000",
                start_date=int(datetime.datetime.now().timestamp()),
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
                start_date=int(datetime.datetime.now().timestamp()),
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
            start_date=int(datetime.datetime.now().timestamp()),
        )
        self.assertTrue(tx.is_valid())
