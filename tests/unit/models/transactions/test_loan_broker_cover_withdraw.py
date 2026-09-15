from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import LoanBrokerCoverWithdraw

_ACCOUNT = "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW"
_LOAN_BROKER_ID = "DB303FC1C7611B22C09E773B51044F6BEA02EF917DF59A2E2860871E167066A5"
_DESTINATION = "rf7HPydP4ihkFkSRHWFq34b4SXRc7GvPCR"
_DESTINATION_TAG = 2345
_CREDENTIAL_ID = "0F0B70F4F4C5B27E39D62D4D69E9DF3D0BC0AC29B8FE7CD5AF1AC8C15F1D2E3B"


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

    def test_valid_with_credential_ids(self):
        tx = LoanBrokerCoverWithdraw(
            account=_ACCOUNT,
            loan_broker_id=_LOAN_BROKER_ID,
            amount="1000",
            destination=_DESTINATION,
            credential_ids=[_CREDENTIAL_ID],
        )
        self.assertTrue(tx.is_valid())

    def test_invalid_duplicate_credential_ids(self):
        with self.assertRaises(XRPLModelException) as e:
            LoanBrokerCoverWithdraw(
                account=_ACCOUNT,
                loan_broker_id=_LOAN_BROKER_ID,
                amount="1000",
                destination=_DESTINATION,
                credential_ids=[_CREDENTIAL_ID, _CREDENTIAL_ID],
            )
        self.assertEqual(
            e.exception.args[0],
            str(
                {
                    "credential_ids_duplicates": "CredentialIDs list cannot contain "
                    "duplicate values."
                }
            ),
        )

    def test_valid_minimal_fields(self):
        tx = LoanBrokerCoverWithdraw(
            account=_ACCOUNT,
            loan_broker_id=_LOAN_BROKER_ID,
            amount="1000",
        )
        self.assertTrue(tx.is_valid())
