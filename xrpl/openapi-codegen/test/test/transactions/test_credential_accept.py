import unittest

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.credential_accept import CredentialAccept

class TestCredentialAccept(unittest.TestCase):
    def test_tx_invalid_missing_required_param_credential_type(self):
        with self.assertRaises(XRPLModelException) as err:
            CredentialAccept(
               account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
               issuer="AAAAA"
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_invalid_credential_type_too_long(self):
        with self.assertRaises(XRPLModelException) as err:
            CredentialAccept(
               account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
               credential_type="eee1865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
               issuer="AAAAA"
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_invalid_credential_type_too_short(self):
        with self.assertRaises(XRPLModelException) as err:
            CredentialAccept(
               account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
               credential_type="",
               issuer="AAAAA"
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_invalid_account_is_not_xrp_account(self):
        with self.assertRaises(XRPLModelException) as err:
            CredentialAccept(
               account="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE",
               credential_type="eee1865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a",
               issuer="AAAAA"
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_valid_transaction(self):
        tx = CredentialAccept(
            account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
            credential_type="eee1865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a",
            issuer="AAAAA"
        )
        self.assertTrue(tx.is_valid())
