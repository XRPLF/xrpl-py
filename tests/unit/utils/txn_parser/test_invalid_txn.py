from __future__ import annotations

from copy import deepcopy
from unittest import TestCase

import xrpl.utils
from tests.unit.utils.txn_parser.transaction import TXN

meta_not_included_txn = deepcopy(TXN)
meta_not_included_txn.pop("meta")
no_nodes_txn = deepcopy(TXN)
no_nodes_txn["meta"].clear()


class TestInvalidTxn(TestCase):
    def test_meta_not_included(self: TestInvalidTxn):
        with self.assertRaises(xrpl.utils.XRPLTxnFieldsException):
            xrpl.utils.parse_balance_changes(transaction=meta_not_included_txn)

    def test_no_nodes(self: TestInvalidTxn):
        with self.assertRaises(xrpl.utils.XRPLTxnFieldsException):
            xrpl.utils.parse_balance_changes(transaction=no_nodes_txn)
