from unittest import TestCase

from tests.integration.it_utils import JSON_RPC_CLIENT
from xrpl.models.requests import Ledger


class TestLedger(TestCase):
    def test_basic_functionality(self):
        response = JSON_RPC_CLIENT.request(Ledger())
        self.assertTrue(response.is_successful())
