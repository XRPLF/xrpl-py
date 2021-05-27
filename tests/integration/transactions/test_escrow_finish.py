try:
    from unittest import IsolatedAsyncioTestCase
except ImportError:
    from aiounittest import AsyncTestCase as IsolatedAsyncioTestCase

from tests.integration.it_utils import submit_transaction_async, test_async_and_sync
from tests.integration.reusable_values import WALLET
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import EscrowFinish

# Special fee for EscrowFinish transactions that contain a fulfillment.
# See note here: https://xrpl.org/escrowfinish.html
FEE = "600000000"

ACCOUNT = WALLET.classic_address
OWNER = "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn"
OFFER_SEQUENCE = 7
CONDITION = (
    "A0258020E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855810100"
)
FULFILLMENT = "A0028000"


class TestEscrowFinish(IsolatedAsyncioTestCase):
    @test_async_and_sync(globals())
    async def test_all_fields(self, client):
        escrow_finish = EscrowFinish(
            account=ACCOUNT,
            sequence=WALLET.sequence,
            owner=OWNER,
            offer_sequence=OFFER_SEQUENCE,
            condition=CONDITION,
            fulfillment=FULFILLMENT,
        )
        response = await submit_transaction_async(escrow_finish, WALLET)
        # Actual engine_result will be 'tecNO_TARGET' since using non-extant
        # account for OWNER
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
