from unittest import TestCase

from tests.integration.it_utils import JSON_RPC_CLIENT
from tests.integration.reusable_values import WALLET
from xrpl.models.requests import AccountInfo


class TestAccountInfo(TestCase):
    def test_basic_functionality(self):
        response = JSON_RPC_CLIENT.request(
            AccountInfo(
                account=WALLET.classic_address,
            )
        )
        self.assertTrue(response.is_successful())
