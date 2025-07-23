import unittest

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.payment_channel_create import PaymentChannelCreate


class TestPaymentChannelCreate(unittest.TestCase):
    def test_tx_invalid_missing_required_param_amount(self):
        with self.assertRaises(XRPLModelException) as err:
            PaymentChannelCreate(
                account="rJ73aumLPTQQmy5wnGhvrogqf5DDhjuzc9",
                cancel_after=5,
                destination="AAAAA",
                destination_tag=5,
                public_key="AAAAA",
                settle_delay=5,
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_invalid_duplicate_destination_and_account(self):
        with self.assertRaises(XRPLModelException) as err:
            PaymentChannelCreate(
                account="rJ73aumLPTQQmy5wnGhvrogqf5DDhjuzc9",
                amount="AAAAA",
                cancel_after=5,
                destination="rJ73aumLPTQQmy5wnGhvrogqf5DDhjuzc9",
                destination_tag=5,
                public_key="AAAAA",
                settle_delay=5,
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_invalid_account_is_not_xrp_account(self):
        with self.assertRaises(XRPLModelException) as err:
            PaymentChannelCreate(
                account="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE",
                amount="AAAAA",
                cancel_after=5,
                destination="AAAAA",
                destination_tag=5,
                public_key="AAAAA",
                settle_delay=5,
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_valid_transaction(self):
        tx = PaymentChannelCreate(
            account="rJ73aumLPTQQmy5wnGhvrogqf5DDhjuzc9",
            amount="AAAAA",
            cancel_after=5,
            destination="AAAAA",
            destination_tag=5,
            public_key="AAAAA",
            settle_delay=5,
        )
        self.assertTrue(tx.is_valid())
