from unittest import TestCase

from tests.integration.it_utils import (
    generate_faucet_wallet,
    get_fee,
    submit_transaction,
)
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import AccountSet
from xrpl.network_clients import JsonRpcClient

JSON_RPC_URL = "http://test.xrp.xpring.io:51234"
JSON_RPC_CLIENT = JsonRpcClient(JSON_RPC_URL)

WALLET = generate_faucet_wallet()

ACCOUNT = WALLET.classic_address
FEE = get_fee()
SEQUENCE = WALLET.next_sequence_num


class TestAccountSet(TestCase):
    def test_required_fields(self):
        set_flag = 3
        account_set = AccountSet(
            account=ACCOUNT, fee=FEE, sequence=SEQUENCE, set_flag=set_flag
        )
        response = submit_transaction(account_set, WALLET)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
