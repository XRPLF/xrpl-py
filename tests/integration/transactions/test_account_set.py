from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import WALLET
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


class TestAccountSet(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_required_fields_and_set_flag(self, client):
        account_set = AccountSet(
            account=ACCOUNT,
            set_flag=SET_FLAG,
        )
        response = await sign_and_reliable_submission_async(account_set, WALLET, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

    @test_async_and_sync(globals())
    async def test_all_fields_minus_set_flag(self, client):
        account_set = AccountSet(
            account=ACCOUNT,
            clear_flag=CLEAR_FLAG,
            domain=DOMAIN,
            email_hash=EMAIL_HASH,
            message_key=MESSAGE_KEY,
            transfer_rate=TRANSFER_RATE,
            tick_size=TICK_SIZE,
        )
        response = await sign_and_reliable_submission_async(account_set, WALLET, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")
