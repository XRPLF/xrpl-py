from unittest import TestCase

from xrpl.models.ledger.account_root_object import AccountRootObject


class TestLedgerObj(TestCase):
    def test_compile(self):
        obj = AccountRootObject("address", "balance", 0, "index", 0, "prv_id", 0, 0)
        assert obj.type == "AccountRoot"
