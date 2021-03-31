from unittest import TestCase

from tests.integration.it_utils import JSON_RPC_CLIENT
from xrpl.models.requests import ServerInfo


class TestServerInfo(TestCase):
    def test_basic_functionality(self):
        response = JSON_RPC_CLIENT.request(ServerInfo())
        self.assertTrue(response.is_successful())
