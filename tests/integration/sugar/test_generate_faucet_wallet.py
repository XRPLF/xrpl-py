from unittest import TestCase

from xrpl.clients import WebsocketClient
from xrpl.wallet.wallet_generation import generate_faucet_wallet


class TestGenerateFaucetWallet(TestCase):
    def test_faucet_host(self):
        with WebsocketClient("wss://hooks-testnet-v3.xrpl-labs.com") as client:
            with self.assertRaises(Exception):
                wallet = generate_faucet_wallet(
                    client, debug=True, faucet_host="https://abcd.com/accounts"
                )
                self.assertEqual(wallet, None)
