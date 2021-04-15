from unittest import TestCase

from tests.integration.it_utils import submit_transaction
from tests.integration.reusable_values import WALLET
from xrpl.models.exceptions import XRPLException
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import AccountSet

ACCOUNT = WALLET.classic_address

CLEAR_FLAG = 3
DOMAIN = "6578616D706C652E636F6D".lower()
EMAIL_HASH = "10000000002000000000300000000012"
MESSAGE_KEY = "03AB40A0490F9B7ED8DF29D246BF2D6269820A0EE7742ACDD457BEA7C7D0931EDB"
SET_FLAG = 8
TRANSFER_RATE = 0
TICK_SIZE = 10
FEE = "3000000"


class TestAccountSet(TestCase):
    def test_required_fields_and_set_flag(self):
        account_set = AccountSet(
            account=ACCOUNT,
            sequence=WALLET.sequence,
            set_flag=SET_FLAG,
        )
        response = submit_transaction(account_set, WALLET)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")
        WALLET.sequence += 1

    def test_all_fields_minus_set_flag(self):
        account_set = AccountSet(
            account=ACCOUNT,
            sequence=WALLET.sequence,
            clear_flag=CLEAR_FLAG,
            domain=DOMAIN,
            email_hash=EMAIL_HASH,
            message_key=MESSAGE_KEY,
            transfer_rate=TRANSFER_RATE,
            tick_size=TICK_SIZE,
        )
        response = submit_transaction(account_set, WALLET)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")
        WALLET.sequence += 1

    def test_high_fee_unauthorized(self):
        # GIVEN a new AccountSet transaction
        account_set = AccountSet(
            account=ACCOUNT,
            sequence=WALLET.sequence,
            clear_flag=CLEAR_FLAG,
            domain=DOMAIN,
            email_hash=EMAIL_HASH,
            message_key=MESSAGE_KEY,
            transfer_rate=TRANSFER_RATE,
            tick_size=TICK_SIZE,
            # WITH fee higher than 2 XRP
            fee=FEE,
        )
        # We expect an XRPLException to be raised
        with self.assertRaises(XRPLException):
            # WITH the default Json RPC Client which doesn't
            # allow more than 2 XRP fee
            submit_transaction(account_set, WALLET)
