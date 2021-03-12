from unittest import TestCase

from tests.integration.it_utils import submit_transaction
from tests.integration.transactions.reusable_values import FEE, WALLET
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import EscrowCancel
from xrpl.network_clients import JsonRpcClient

JSON_RPC_URL = "http://test.xrp.xpring.io:51234"
JSON_RPC_CLIENT = JsonRpcClient(JSON_RPC_URL)

ACCOUNT = WALLET.classic_address
OWNER = "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn"
OFFER_SEQUENCE = 7


class TestEscrowCancel(TestCase):
    def test_all_fields(self):
        escrow_cancel = EscrowCancel(
            account=ACCOUNT,
            fee=FEE,
            sequence=WALLET.next_sequence_num,
            owner=OWNER,
            offer_sequence=OFFER_SEQUENCE,
        )
        response = submit_transaction(escrow_cancel, WALLET)
        # Actual engine_result is `tecNO_TARGET since OWNER account doesn't exist
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
