from unittest import TestCase

from xrpl.models.amounts import IssuedCurrencyAmount, MPTAmount
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import LoanBrokerCoverClawback

_SOURCE = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_ISSUER = "rHxTJLqdVUxjJuZEZvajXYYQJ7q8p4DhHy"


class TestLoanBrokerCoverClawback(TestCase):
    def test_invalid_no_amount_nor_loan_broker_id_specified(self):
        with self.assertRaises(XRPLModelException) as error:
            LoanBrokerCoverClawback(account=_SOURCE)
        self.assertEqual(
            error.exception.args[0],
            "{'LoanBrokerCoverClawback': 'No amount or loan broker ID specified.'}",
        )

    def test_invalid_xrp_amount(self):
        with self.assertRaises(XRPLModelException) as error:
            LoanBrokerCoverClawback(account=_SOURCE, amount="10.20")
        self.assertEqual(
            error.exception.args[0],
            "{'amount': \"amount is <class 'str'>, expected "
            + "typing.Union[xrpl.models.amounts.issued_currency_amount"
            + ".IssuedCurrencyAmount, xrpl.models.amounts.mpt_amount.MPTAmount, "
            + "NoneType]\", 'LoanBrokerCoverClawback:Amount': 'Amount cannot be XRP.'}",
        )

    def test_invalid_negative_amount(self):
        with self.assertRaises(XRPLModelException) as error:
            LoanBrokerCoverClawback(
                account=_SOURCE,
                amount=IssuedCurrencyAmount(
                    issuer=_ISSUER,
                    currency="USD",
                    value="-10",
                ),
            )
        self.assertEqual(
            error.exception.args[0],
            "{'LoanBrokerCoverClawback:Amount': 'Amount must be greater than 0.'}",
        )

    def test_valid_loan_broker_cover_clawback(self):
        tx = LoanBrokerCoverClawback(
            account=_SOURCE,
            amount=MPTAmount(
                mpt_issuance_id="00000001A407AF5856CECE4281FED12B7B179B49A4AEF506",
                value="10.20",
            ),
            loan_broker_id=_ISSUER,
        )
        self.assertTrue(tx.is_valid())
