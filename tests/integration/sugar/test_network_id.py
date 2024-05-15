from unittest import TestCase

from xrpl.asyncio.transaction.main import _RESTRICTED_NETWORKS
from xrpl.clients import WebsocketClient
from xrpl.models.transactions import AccountSet
from xrpl.transaction import autofill
from xrpl.wallet.wallet_generation import generate_faucet_wallet

_FEE = "0.00001"


# TODO: move to test_transaction and use the standard integration test setup
class TestNetworkID(TestCase):
    # Autofill should override tx networkID for network with ID > 1024
    # and build_version from 1.11.0 or later.
    def test_networkid_override(self):
        with WebsocketClient("wss://s.altnet.rippletest.net:51233") as client:
            wallet = generate_faucet_wallet(client, debug=True)
            tx = AccountSet(
                account=wallet.classic_address,
                fee=_FEE,
                domain="www.example.com",
            )
            tx_autofilled = autofill(tx, client)
            self.assertGreaterEqual(client.network_id, _RESTRICTED_NETWORKS)
            self.assertEqual(tx_autofilled.network_id, client.network_id)
