from unittest import TestCase
from xrpl.asyncio.transaction.main import _RESTRICTED_NETWORKS
from xrpl.clients import JsonRpcClient, WebsocketClient

from xrpl.models.transactions import AccountSet
from xrpl.transaction import autofill
from xrpl.wallet.wallet_generation import generate_faucet_wallet

_FEE = "0.00001"

class TestAutofill(TestCase):
  # Autofill should override tx networkID for network with ID > 1024 and build_version from 1.11.0 or later.
  def test_networkid_override(self):
    client = JsonRpcClient('https://sidechain-net1.devnet.rippletest.net:51234')
    wallet = generate_faucet_wallet(client, debug=True)
    # Override client's build_version since 1.11.0 is not released yet.
    client.build_version = '1.11.0'
    tx = AccountSet(
            account=wallet.classic_address,
            fee=_FEE,
            domain='www.example.com',
        )
    tx_autofilled = autofill(tx, client)
    self.assertGreaterEqual(client.network_id, _RESTRICTED_NETWORKS)
    self.assertEqual(tx_autofilled.network_id, client.network_id)
  
  # Autofill should ignore tx network_id for build version earlier than 1.11.0.
  def test_networkid_ignore_early_version(self):
    client = JsonRpcClient('https://sidechain-net1.devnet.rippletest.net:51234')
    wallet = generate_faucet_wallet(client, debug=True)
    # Override client's build_version since 1.11.0 is not released yet.
    client.build_version = '1.10.0'
    tx = AccountSet(
            account=wallet.classic_address,
            fee=_FEE,
            domain='www.example.com',
        )
    tx_autofilled = autofill(tx, client)
    self.assertEqual(tx_autofilled.network_id, None)
  
  # Autofill should ignore tx network_id for networks with ID <= 1024.
  def test_networkid_ignore_restricted_networks(self):
    client = JsonRpcClient('https://s.altnet.rippletest.net:51234')
    wallet = generate_faucet_wallet(client, debug=True)
    # Override client's build_version since 1.11.0 is not released yet.
    client.build_version = '1.11.0'
    tx = AccountSet(
            account=wallet.classic_address,
            fee=_FEE,
            domain='www.example.com',
        )
    tx_autofilled = autofill(tx, client)
    self.assertLessEqual(client.network_id, _RESTRICTED_NETWORKS)
    self.assertEqual(tx_autofilled.network_id, None)

  # Autofill should override tx networkID for hooks-testnet.
  def test_networkid_override(self):
    with WebsocketClient("wss://hooks-testnet-v3.xrpl-labs.com") as client:
      wallet = generate_faucet_wallet(client, debug=True)
      tx = AccountSet(
              account=wallet.classic_address,
              fee=_FEE,
              domain='www.example.com',
          )
      tx_autofilled = autofill(tx, client)
      self.assertEqual(tx_autofilled.network_id, client.network_id)