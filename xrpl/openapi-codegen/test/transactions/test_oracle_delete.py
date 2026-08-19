import unittest

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.oracle_delete import OracleDelete


class TestOracleDelete(unittest.TestCase):
    def test_tx_invalid_missing_required_param_oracle_document_id(self):
        with self.assertRaises(XRPLModelException) as err:
            OracleDelete(account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh")
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_invalid_account_is_not_xrp_account(self):
        with self.assertRaises(XRPLModelException) as err:
            OracleDelete(
                account="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE", oracle_document_id="AAAAA"
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_valid_transaction(self):
        tx = OracleDelete(
            account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh", oracle_document_id="AAAAA"
        )
        self.assertTrue(tx.is_valid())
