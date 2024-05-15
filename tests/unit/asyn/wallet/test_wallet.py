from unittest import TestCase

from xrpl.asyncio.wallet.wallet_generation import (
    _DEV_FAUCET_URL,
    _TEST_FAUCET_URL,
    get_faucet_url,
    process_faucet_host_url,
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


class TestProcessFaucetHostURL(TestCase):
    """Test process_faucet_host_url."""

    def test_process_faucet_host_url_no_protocol(self) -> None:
        """Test with domain only, no protocol. Lacks a protocol and path, so it
        defaults to https://abcd.com/accounts"""
        input_url = "faucet.devnet.rippletest.net"
        expected_url = "https://faucet.devnet.rippletest.net/accounts"
        self.assertEqual(process_faucet_host_url(input_url), expected_url)

    def test_process_faucet_host_url_with_https(self) -> None:
        """Test with HTTPS protocol specified. Has a complete URL but lacks a path,
        thus "/accounts" is appended."""
        input_url = "https://faucet.devnet.rippletest.net"
        expected_url = "https://faucet.devnet.rippletest.net/accounts"
        self.assertEqual(process_faucet_host_url(input_url), expected_url)

    def test_process_faucet_host_url_with_path(self) -> None:
        """Test with domain and path, no protocol. Lacks a protocol, defaults to
        "https://", and already specifies a path."""
        input_url = "faucet.devnet.rippletest.net/accounts"
        expected_url = "https://faucet.devnet.rippletest.net/accounts"
        self.assertEqual(process_faucet_host_url(input_url), expected_url)

    def test_process_faucet_host_url_full(self) -> None:
        """Test with full URL."""
        input_url = "https://faucet.devnet.rippletest.net/accounts"
        expected_url = "https://faucet.devnet.rippletest.net/accounts"
        self.assertEqual(process_faucet_host_url(input_url), expected_url)

    def test_process_faucet_host_url_different_protocol(self) -> None:
        """Test with a non-HTTP protocol specified."""
        input_url = "ftp://faucet.devnet.rippletest.net"
        expected_url = "ftp://faucet.devnet.rippletest.net/accounts"
        self.assertEqual(process_faucet_host_url(input_url), expected_url)

    def test_process_faucet_host_url_trailing_slash(self) -> None:
        """Test with a non-HTTP protocol specified."""
        input_url = "https://faucet.devnet.rippletest.net/"
        expected_url = "https://faucet.devnet.rippletest.net/accounts"
        self.assertEqual(process_faucet_host_url(input_url), expected_url)

    def test_process_faucet_host_url_custom_path(self) -> None:
        """Test with a non-HTTP protocol specified."""
        input_url = "https://faucet.devnet.rippletest.net/america/"
        expected_url = "https://faucet.devnet.rippletest.net/america"
        self.assertEqual(process_faucet_host_url(input_url), expected_url)
