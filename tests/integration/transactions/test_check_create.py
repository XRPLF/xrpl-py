from unittest import TestCase

from tests.integration.it_utils import generate_faucet_wallet, submit_transaction
from tests.integration.transactions.reusable_values import FEE, WALLET
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import CheckCreate
from xrpl.network_clients import JsonRpcClient

JSON_RPC_URL = "http://test.xrp.xpring.io:51234"
JSON_RPC_CLIENT = JsonRpcClient(JSON_RPC_URL)

ACCOUNT = WALLET.classic_address
DESTINATION = generate_faucet_wallet().classic_address
DESTINATION_TAG = 1
SENDMAX = "100000000"
EXPIRATION = 970113521
INVOICE_ID = "6F1DFD1D0FE8A32E40E1F2C05CF1C15545BAB56B617F9C6C2D63A6B704BEF59B"


class TestCheckCreate(TestCase):
    def test_all_fields(self):
        check_create = CheckCreate(
            account=ACCOUNT,
            fee=FEE,
            sequence=WALLET.next_sequence_num,
            destination=DESTINATION,
            destination_tag=DESTINATION_TAG,
            send_max=SENDMAX,
            expiration=EXPIRATION,
            invoice_id=INVOICE_ID,
        )
        response = submit_transaction(check_create, WALLET)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")
