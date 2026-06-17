from unittest import TestCase

from xrpl.models.transactions import LoanBrokerCoverWithdraw

_ACCOUNT = "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW"
_LOAN_BROKER_ID = "DB303FC1C7611B22C09E773B51044F6BEA02EF917DF59A2E2860871E167066A5"
_DESTINATION = "rf7HPydP4ihkFkSRHWFq34b4SXRc7GvPCR"
_DESTINATION_TAG = 2345


class TestLoanBrokerCoverWithdraw(TestCase):
    def test_valid(self):
        tx = LoanBrokerCoverWithdraw(
            account=_ACCOUNT,
            loan_broker_id=_LOAN_BROKER_ID,
            amount="1000",
            destination=_DESTINATION,
            destination_tag=_DESTINATION_TAG,
        )
        self.assertTrue(tx.is_valid())

    def test_valid_minimal_fields(self):
        tx = LoanBrokerCoverWithdraw(
            account=_ACCOUNT,
            loan_broker_id=_LOAN_BROKER_ID,
            amount="1000",
        )
        self.assertTrue(tx.is_valid())
