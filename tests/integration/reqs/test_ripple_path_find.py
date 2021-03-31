from unittest import TestCase

from tests.integration.it_utils import JSON_RPC_CLIENT
from tests.integration.reusable_values import DESTINATION, WALLET
from xrpl.models.requests import RipplePathFind


class TestRipplePathFind(TestCase):
    def test_basic_functionality(self):
        response = JSON_RPC_CLIENT.request(
            RipplePathFind(
                source_account=WALLET.classic_address,
                destination_account=DESTINATION.classic_address,
                destination_amount="100",
            ),
        )
        self.assertTrue(response.is_successful())
