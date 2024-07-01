from unittest import TestCase

from xrpl.clients import WebsocketClient
from xrpl.models.transactions import AccountSet
from xrpl.transaction import autofill

_FEE = "0.00001"


# TODO: move to test_transaction and use the standard integration test setup
class TestNetworkID(TestCase):
    # Autofill should populate the tx networkID and build_version from 1.11.0 or later.
    def test_autofill_populate_networkid(self):
        with WebsocketClient("wss://s.altnet.rippletest.net:51233") as client:
            tx = AccountSet(
                account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
                fee=_FEE,
                domain="www.example.com",
            )
            autofill(tx, client)
            self.assertEqual(client.network_id, 1)

            # the build_version changes with newer releases of rippled
            self.assertNotEqual(client.build_version, None)
