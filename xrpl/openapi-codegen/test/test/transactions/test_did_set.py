import unittest

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.did_set import DIDSet

class TestDIDSet(unittest.TestCase):
    def test_tx_invalid_missing_required_param_account(self):
        with self.assertRaises(XRPLModelException) as err:
            DIDSet(
               data="eee1865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a",
               did_document="eee1865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a",
               uri="eee1865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a"
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_invalid_require_one_of_missing_data_did_document_uri(self):
        with self.assertRaises(XRPLModelException) as err:
            DIDSet(
               account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_invalid_did_document_too_long(self):
        with self.assertRaises(XRPLModelException) as err:
            DIDSet(
               account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
               data="eee1865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a",
               did_document="eee1865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
               uri="eee1865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a"
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_invalid_data_too_long(self):
        with self.assertRaises(XRPLModelException) as err:
            DIDSet(
               account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
               data="eee1865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
               did_document="eee1865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a",
               uri="eee1865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a"
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_invalid_uri_too_long(self):
        with self.assertRaises(XRPLModelException) as err:
            DIDSet(
               account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
               data="eee1865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a",
               did_document="eee1865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a",
               uri="eee1865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_invalid_account_is_not_xrp_account(self):
        with self.assertRaises(XRPLModelException) as err:
            DIDSet(
               account="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE",
               data="eee1865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a",
               did_document="eee1865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a",
               uri="eee1865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a"
            )
        self.assertIsNotNone(err.exception.args[0])
    def test_tx_valid_transaction(self):
        tx = DIDSet(
            account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
            data="eee1865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a",
            did_document="eee1865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a",
            uri="eee1865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a"
        )
        self.assertTrue(tx.is_valid())
