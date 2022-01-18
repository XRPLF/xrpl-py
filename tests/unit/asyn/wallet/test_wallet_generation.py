from unittest import TestCase

from xrpl.asyncio.wallet.wallet_generation import get_faucet_url


class TestWallet(TestCase):
    def test_get_faucet_wallet_dev(self):
        json_client_url = "https://s.devnet.rippletest.net:51234"
        ws_client_url = "wss://s.devnet.rippletest.net/"
        expected_faucet = "https://faucet.devnet.rippletest.net/accounts"

        self.assertEqual(get_faucet_url(json_client_url), expected_faucet)
        self.assertEqual(get_faucet_url(ws_client_url), expected_faucet)

    def test_get_faucet_wallet_custom(self):
        json_client_url = "https://s.devnet.rippletest.net:51234"
        ws_client_url = "wss://s.devnet.rippletest.net/"
        custom_host = "my_host.org"
        expected_faucet = "https://my_host.org/accounts"

        self.assertEqual(get_faucet_url(json_client_url, custom_host), expected_faucet)
        self.assertEqual(get_faucet_url(ws_client_url, custom_host), expected_faucet)
