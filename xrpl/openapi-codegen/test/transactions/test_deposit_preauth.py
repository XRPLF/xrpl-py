import unittest

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.deposit_preauth import Credential
from xrpl.models.transactions.deposit_preauth import DepositPreauth


class TestDepositPreauth(unittest.TestCase):
    def test_tx_invalid_missing_required_param_account(self):
        with self.assertRaises(XRPLModelException) as err:
            DepositPreauth(authorize="AAAAA")
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_invalid_require_exactly_one_authorize_authorize_credentials_unauthorize_unauthorize_credentials(
        self,
    ):
        with self.assertRaises(XRPLModelException) as err:
            DepositPreauth(
                account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
                authorize="AAAAA",
                authorize_credentials=[
                    Credential(
                        credential_type="eee1865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a",
                        issuer="AAAAA",
                    )
                ],
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_invalid_account_is_not_xrp_account(self):
        with self.assertRaises(XRPLModelException) as err:
            DepositPreauth(
                account="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE", authorize="AAAAA"
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_valid_transaction(self):
        tx = DepositPreauth(
            account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh", authorize="AAAAA"
        )
        self.assertTrue(tx.is_valid())
