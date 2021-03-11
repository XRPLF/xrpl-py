from unittest import TestCase

from tests.integration.it_utils import JSON_RPC_CLIENT, submit_transaction
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import AccountSet
from xrpl.wallet import generate_faucet_wallet, get_fee

WALLET = generate_faucet_wallet(JSON_RPC_CLIENT)

ACCOUNT = WALLET.classic_address
FEE = get_fee(JSON_RPC_CLIENT)
SEQUENCE = WALLET.next_sequence_num


class TestAccountSet(TestCase):
    def test_required_fields(self):
        set_flag = 3
        account_set = AccountSet(
            account=ACCOUNT, fee=FEE, sequence=SEQUENCE, set_flag=set_flag
        )
        response = submit_transaction(account_set, WALLET)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
