from unittest import TestCase

from tests.integration.it_utils import JSON_RPC_CLIENT
from tests.integration.reusable_values import WALLET
from xrpl.account import does_account_exist


class TestAccount(TestCase):
    def test_does_account_exist_true(self):
        self.assertTrue(does_account_exist(WALLET.classic_address, JSON_RPC_CLIENT))

    def test_does_account_exist_false(self):
        address = "rG1QQv2nh2gr7RCZ1P8YYcBUcCCN633jCn"
        self.assertFalse(does_account_exist(address, JSON_RPC_CLIENT))
