import unittest

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.check_create import CheckCreate


class TestCheckCreate(unittest.TestCase):
    def test_tx_invalid_missing_required_param_destination(self):
        with self.assertRaises(XRPLModelException) as err:
            CheckCreate(
                account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
                destination_tag=5,
                expiration=5,
                invoice_id="2561865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a",
                send_max="12345",
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_invalid_account_is_not_xrp_account(self):
        with self.assertRaises(XRPLModelException) as err:
            CheckCreate(
                account="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE",
                destination="AAAAA",
                destination_tag=5,
                expiration=5,
                invoice_id="2561865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a",
                send_max="12345",
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_valid_transaction(self):
        tx = CheckCreate(
            account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
            destination="AAAAA",
            destination_tag=5,
            expiration=5,
            invoice_id="2561865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a",
            send_max="12345",
        )
        self.assertTrue(tx.is_valid())
