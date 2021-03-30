from unittest import TestCase

from tests.integration.it_utils import submit_transaction
from xrpl.clients import JsonRpcClient
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import AccountSet, Payment
from xrpl.wallet import generate_faucet_wallet

DEV_JSON_RPC_URL = "https://s.devnet.rippletest.net:51234"
DEV_JSON_RPC_CLIENT = JsonRpcClient(DEV_JSON_RPC_URL)


class TestWallet(TestCase):
    def test_generate_faucet_wallet_dev(self):
        wallet = generate_faucet_wallet(DEV_JSON_RPC_CLIENT)
        account_set = AccountSet(
            account=wallet.classic_address,
            fee="10",
            sequence=wallet.next_sequence_num,
            set_flag=3,
        )
        response = submit_transaction(account_set, wallet, client=DEV_JSON_RPC_CLIENT)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

    def test_generate_faucet_wallet_rel_sub(self):
        destination = generate_faucet_wallet(DEV_JSON_RPC_CLIENT)
        wallet = generate_faucet_wallet(DEV_JSON_RPC_CLIENT)
        response = submit_transaction(
            Payment(
                account=wallet.classic_address,
                sequence=wallet.next_sequence_num,
                fee="10",
                amount="1",
                destination=destination.classic_address,
            ),
            wallet,
            client=DEV_JSON_RPC_CLIENT,
        )
        self.assertTrue(response.is_successful())
