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
            "{'LoanSet:data': 'Data must be no longer than 256 bytes.'}",
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
            "{'LoanSet:GracePeriod': 'Grace period must be between 60 seconds and the "
            + "payment interval (60 seconds if omitted) inclusive.'}",
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

    def test_grace_period_bounds(self):
        grace_period_error = (
            "{'LoanSet:GracePeriod': 'Grace period must be between 60 seconds and the "
            "payment interval (60 seconds if omitted) inclusive.'}"
        )
        for payment_interval, grace_period in [(120, 60), (120, 120), (None, 60)]:
            tx = LoanSet(
                account=_SOURCE,
                loan_broker_id=_ISSUER,
                principal_requested="100000000",
                payment_interval=payment_interval,
                grace_period=grace_period,
            )
            self.assertTrue(tx.is_valid())

        # Without payment_interval, rippled uses its default of 60
        for payment_interval, grace_period in [(120, 59), (None, 61)]:
            with self.assertRaises(XRPLModelException) as error:
                LoanSet(
                    account=_SOURCE,
                    loan_broker_id=_ISSUER,
                    principal_requested="100000000",
                    payment_interval=payment_interval,
                    grace_period=grace_period,
                )
            self.assertEqual(error.exception.args[0], grace_period_error)

    def test_invalid_payment_total_zero(self):
        with self.assertRaises(XRPLModelException) as error:
            LoanSet(
                account=_SOURCE,
                loan_broker_id=_ISSUER,
                principal_requested="100000000",
                payment_total=0,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'LoanSet:payment_total': 'Payment total must be greater than 0.'}",
        )

    def test_invalid_principal_requested_not_positive(self):
        for principal_requested in ["0", "-1"]:
            with self.assertRaises(XRPLModelException) as error:
                LoanSet(
                    account=_SOURCE,
                    loan_broker_id=_ISSUER,
                    principal_requested=principal_requested,
                )
            self.assertEqual(
                error.exception.args[0],
                "{'LoanSet:principal_requested': 'Principal requested must be "
                "greater than 0.'}",
            )

    def test_loan_origination_fee_bounds(self):
        for principal_requested, loan_origination_fee in [
            ("100000", "0"),
            ("100000", "100000"),
            ("1e5", "1e5"),
        ]:
            tx = LoanSet(
                account=_SOURCE,
                loan_broker_id=_ISSUER,
                principal_requested=principal_requested,
                loan_origination_fee=loan_origination_fee,
            )
            self.assertTrue(tx.is_valid())

        for loan_origination_fee in ["100001", "-1"]:
            with self.assertRaises(XRPLModelException) as error:
                LoanSet(
                    account=_SOURCE,
                    loan_broker_id=_ISSUER,
                    principal_requested="100000",
                    loan_origination_fee=loan_origination_fee,
                )
            self.assertEqual(
                error.exception.args[0],
                "{'LoanSet:loan_origination_fee': 'Loan origination fee must be "
                "between 0 and the principal requested inclusive.'}",
            )

    def test_invalid_negative_payment_fees(self):
        for field_name, label in [
            ("loan_service_fee", "Loan service fee"),
            ("late_payment_fee", "Late payment fee"),
            ("close_payment_fee", "Close payment fee"),
        ]:
            tx = LoanSet(
                account=_SOURCE,
                loan_broker_id=_ISSUER,
                principal_requested="100000000",
                **{field_name: "0"},
            )
            self.assertTrue(tx.is_valid())

            with self.assertRaises(XRPLModelException) as error:
                LoanSet(
                    account=_SOURCE,
                    loan_broker_id=_ISSUER,
                    principal_requested="100000000",
                    **{field_name: "-1"},
                )
            self.assertEqual(
                error.exception.args[0],
                f"{{'LoanSet:{field_name}': '{label} must not be negative.'}}",
            )
