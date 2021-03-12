from unittest import TestCase

from tests.integration.it_utils import submit_transaction
from tests.integration.transactions.reusable_values import FEE, WALLET
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import EscrowCreate
from xrpl.network_clients import JsonRpcClient

JSON_RPC_URL = "http://test.xrp.xpring.io:51234"
JSON_RPC_CLIENT = JsonRpcClient(JSON_RPC_URL)

ACCOUNT = WALLET.classic_address
OWNER = "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn"
OFFER_SEQUENCE = 7

AMOUNT = "10000"
DESTINATION = "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW"
CANCEL_AFTER = 533257958
FINISH_AFTER = 533171558
CONDITION = (
    "A0258020E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855810100"
)
DESTINATION_TAG = 23480
SOURCE_TAG = 11747


class TestEscrowCreate(TestCase):
    def test_all_fields(self):
        escrow_create = EscrowCreate(
            account=ACCOUNT,
            fee=FEE,
            sequence=WALLET.next_sequence_num,
        )
        response = submit_transaction(escrow_create, WALLET)
        print(response)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
