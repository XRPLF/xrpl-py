from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import LoanBrokerSet

_SOURCE = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_VAULT_ID = "DB303FC1C7611B22C09E773B51044F6BEA02EF917DF59A2E2860871E167066A5"


class TestLoanBrokerSet(TestCase):

    def test_invalid_data_too_long(self):
        with self.assertRaises(XRPLModelException) as error:
            LoanBrokerSet(
                account=_SOURCE,
                vault_id=_VAULT_ID,
                data="A" * 257,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'LoanBrokerSet:data': 'Data must be less than 256 bytes.'}",
        )

    def test_invalid_management_fee_rate_too_low(self):
        with self.assertRaises(XRPLModelException) as error:
            LoanBrokerSet(
                account=_SOURCE,
                vault_id=_VAULT_ID,
                management_fee_rate=-1,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'LoanBrokerSet:management_fee_rate': 'Management fee rate must be between"
            + " 0 and 10_000 inclusive.'}",
        )

    def test_invalid_management_fee_rate_too_high(self):

        with self.assertRaises(XRPLModelException) as error:
            LoanBrokerSet(
                account=_SOURCE,
                vault_id=_VAULT_ID,
                management_fee_rate=10001,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'LoanBrokerSet:management_fee_rate': 'Management fee rate must be between"
            + " 0 and 10_000 inclusive.'}",
        )

    def test_invalid_cover_rate_minimum_too_low(self):
        with self.assertRaises(XRPLModelException) as error:
            LoanBrokerSet(
                account=_SOURCE,
                vault_id=_VAULT_ID,
                cover_rate_minimum=-1,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'LoanBrokerSet:cover_rate_minimum': 'Cover rate minimum must be between 0"
            + " and 100_000 inclusive.'}",
        )

    def test_invalid_cover_rate_minimum_too_high(self):
        with self.assertRaises(XRPLModelException) as error:
            LoanBrokerSet(
                account=_SOURCE,
                vault_id=_VAULT_ID,
                cover_rate_minimum=100001,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'LoanBrokerSet:cover_rate_minimum': 'Cover rate minimum must be between 0"
            + " and 100_000 inclusive.'}",
        )

    def test_invalid_cover_rate_liquidation_too_low(self):
        with self.assertRaises(XRPLModelException) as error:
            LoanBrokerSet(
                account=_SOURCE,
                vault_id=_VAULT_ID,
                cover_rate_liquidation=-1,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'LoanBrokerSet:cover_rate_liquidation': 'Cover rate liquidation must be"
            + " between 0 and 100_000 inclusive.'}",
        )

    def test_invalid_cover_rate_liquidation_too_high(self):
        with self.assertRaises(XRPLModelException) as error:
            LoanBrokerSet(
                account=_SOURCE,
                vault_id=_VAULT_ID,
                cover_rate_liquidation=100001,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'LoanBrokerSet:cover_rate_liquidation': 'Cover rate liquidation must be"
            + " between 0 and 100_000 inclusive.'}",
        )

    def test_invalid_debt_maximum_too_low(self):
        with self.assertRaises(XRPLModelException) as error:
            LoanBrokerSet(
                account=_SOURCE,
                vault_id=_VAULT_ID,
                debt_maximum="-1",
            )
        self.assertEqual(
            error.exception.args[0],
            "{'LoanBrokerSet:debt_maximum': 'Debt maximum must not be negative or"
            + " greater than 9223372036854775807.'}",
        )

    def test_invalid_debt_maximum_too_high(self):

        with self.assertRaises(XRPLModelException) as error:
            LoanBrokerSet(
                account=_SOURCE,
                vault_id=_VAULT_ID,
                debt_maximum="9223372036854775808",
            )
        self.assertEqual(
            error.exception.args[0],
            "{'LoanBrokerSet:debt_maximum': 'Debt maximum must not be negative or"
            + " greater than 9223372036854775807.'}",
        )

    def test_valid_loan_broker_set(self):
        tx = LoanBrokerSet(
            account=_SOURCE,
            vault_id=_VAULT_ID,
        )
        self.assertTrue(tx.is_valid())
