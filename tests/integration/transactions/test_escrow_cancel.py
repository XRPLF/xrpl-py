from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import WALLET
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import EscrowCancel

ACCOUNT = WALLET.classic_address
OWNER = "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn"
OFFER_SEQUENCE = 7


class TestEscrowCancel(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_all_fields(self, client):
        escrow_cancel = EscrowCancel(
            account=ACCOUNT,
            owner=OWNER,
            offer_sequence=OFFER_SEQUENCE,
        )
        response = await sign_and_reliable_submission_async(
            escrow_cancel, WALLET, client
        )
        # Actual engine_result is `tecNO_TARGET since OWNER account doesn't exist
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
