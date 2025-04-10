import unittest

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.payment import Payment
from xrpl.models.transactions.payment import PaymentFlag

class TestPayment(unittest.TestCase):
    def test_tx_invalid_account_is_not_xrp_account(self):
        with self.assertRaises(XRPLModelException) as err:
            Payment(
               account="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE",
               amount="12345",
               destination="AAAAA",
               destination_tag=5,
               flags=PaymentFlag.TF_LIMIT_QUALITY,
               invoice_id="AAAAA",
               send_max="12345"
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_valid_transaction(self):
        tx = Payment(
            account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
            amount="12345",
            destination="AAAAA",
            destination_tag=5,
            flags=PaymentFlag.TF_LIMIT_QUALITY,
            invoice_id="AAAAA",
            send_max="12345"
        )
        self.assertTrue(tx.is_valid())
