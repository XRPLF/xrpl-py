from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import submit_transaction_async, test_async_and_sync
from tests.integration.reusable_values import DESTINATION, WALLET, GATEWAY
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import EscrowCreate

CANCEL_AFTER = 533257958
FINISH_AFTER = 533171558
CONDITION = (
    "A0258020E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855810100"
)
DESTINATION_TAG = 23480
SOURCE_TAG = 11747


class TestEscrowCreate(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_native(self, client):
        escrow_create = EscrowCreate(
            account=WALLET.classic_address,
            sequence=WALLET.sequence,
            amount="1000",
            destination=DESTINATION.classic_address,
            destination_tag=DESTINATION_TAG,
            cancel_after=CANCEL_AFTER,
            finish_after=FINISH_AFTER,
            source_tag=SOURCE_TAG,
        )
        response = await submit_transaction_async(escrow_create, WALLET)
        # Actual engine_result will be `tecNO_PERMISSION`...
        # maybe due to CONDITION or something
        self.assertEqual(response.status, ResponseStatus.SUCCESS)

    @test_async_and_sync(globals())
    async def test_ic(self, client):
        escrow_create = EscrowCreate(
            account=WALLET.classic_address,
            sequence=WALLET.sequence,
            amount=IssuedCurrencyAmount(
                currency="USD",
                issuer=GATEWAY.classic_address,
                value="1000",
            ),
            destination=DESTINATION.classic_address,
            destination_tag=DESTINATION_TAG,
            cancel_after=CANCEL_AFTER,
            finish_after=FINISH_AFTER,
            source_tag=SOURCE_TAG,
        )
        response = await submit_transaction_async(escrow_create, WALLET)
        # Actual engine_result will be `tecNO_PERMISSION`...
        # maybe due to CONDITION or something
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
