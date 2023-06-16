from unittest import TestCase

from xrpl.asyncio.wallet.wallet_generation import (
    _AMM_DEV_FAUCET_URL,
    _DEV_FAUCET_URL,
    _HOOKS_V3_TEST_FAUCET_URL,
    _TEST_FAUCET_URL,
    get_faucet_url,
)
from xrpl.core.addresscodec import classic_address_to_xaddress
from xrpl.wallet import Wallet


class TestWallet(TestCase):
    def test_wallet_get_xaddress(self):
        wallet = Wallet.create()
        expected = classic_address_to_xaddress(wallet.classic_address, None, False)
        self.assertEqual(wallet.get_xaddress(), expected)

    def test_get_faucet_wallet_dev(self):
        json_client_url = "https://s.devnet.rippletest.net:51234"
        ws_client_url = "wss://s.devnet.rippletest.net/"
        expected_faucet = _DEV_FAUCET_URL

        self.assertEqual(get_faucet_url(json_client_url), expected_faucet)
        self.assertEqual(get_faucet_url(ws_client_url), expected_faucet)

    def test_get_faucet_wallet_custom(self):
        json_client_url = "https://s.devnet.rippletest.net:51234"
        ws_client_url = "wss://s.devnet.rippletest.net/"
        custom_host = "my_host.org"
        expected_faucet = "https://my_host.org/accounts"

        self.assertEqual(get_faucet_url(json_client_url, custom_host), expected_faucet)
        self.assertEqual(get_faucet_url(ws_client_url, custom_host), expected_faucet)

    def test_get_faucet_wallet_test(self):
        json_client_url = "https://testnet.xrpl-labs.com"
        ws_client_url = "wss://testnet.xrpl-labs.com"
        expected_faucet = _TEST_FAUCET_URL

        self.assertEqual(get_faucet_url(json_client_url), expected_faucet)
        self.assertEqual(get_faucet_url(ws_client_url), expected_faucet)

    def test_get_faucet_wallet_amm_dev(self):
        json_client_url = "https://amm.devnet.rippletest.net:51233"
        ws_client_url = "wss://amm.devnet.rippletest.net:51233"
        expected_faucet = _AMM_DEV_FAUCET_URL

        self.assertEqual(get_faucet_url(json_client_url), expected_faucet)
        self.assertEqual(get_faucet_url(ws_client_url), expected_faucet)

    def test_get_faucet_wallet_hooks_v3_test(self):
        json_client_url = "https://hooks-testnet-v3.xrpl-labs.com"
        ws_client_url = "wss://hooks-testnet-v3.xrpl-labs.com"
        expected_faucet = _HOOKS_V3_TEST_FAUCET_URL

        self.assertEqual(get_faucet_url(json_client_url), expected_faucet)
        self.assertEqual(get_faucet_url(ws_client_url), expected_faucet)
