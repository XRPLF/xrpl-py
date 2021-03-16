from unittest import TestCase

from tests.integration.it_utils import JSON_RPC_CLIENT
from tests.integration.reusable_values import FEE, WALLET
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import AccountSet
from xrpl.reliable_submission import send_reliable_submission

ACCOUNT = WALLET.classic_address

CLEAR_FLAG = 3
DOMAIN = "6578616D706C652E636F6D".lower()
EMAIL_HASH = "10000000002000000000300000000012"
MESSAGE_KEY = "03AB40A0490F9B7ED8DF29D246BF2D6269820A0EE7742ACDD457BEA7C7D0931EDB"
SET_FLAG = 8
TRANSFER_RATE = 0
TICK_SIZE = 10


class TestReliableSubmission(TestCase):
    def test_simple(self):
        account_set = AccountSet(
            account=ACCOUNT,
            fee=FEE,
            sequence=WALLET.next_sequence_num,
            set_flag=SET_FLAG,
            last_ledger_sequence=WALLET.next_sequence_num + 10,
        )
        response = send_reliable_submission(account_set, WALLET, JSON_RPC_CLIENT)
        self.assertTrue(response.result["validated"])
        self.assertEqual(response.result["meta"]["TransactionResult"], "tesSUCCESS")
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
