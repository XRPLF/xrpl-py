from unittest import TestCase

from tests.integration.it_utils import JSON_RPC_CLIENT
from tests.integration.reusable_values import OFFER
from xrpl.models.requests import Tx


class TestTx(TestCase):
    def test_basic_functionality(self):
        response = JSON_RPC_CLIENT.request(
            Tx(
                transaction=OFFER.result["hash"],
            ),
        )
        self.assertTrue(response.is_successful())
