from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import OFFER, WALLET
from xrpl.models.transactions import OfferCancel


class TestOfferCancel(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_all_fields(self, client):
        response = await sign_and_reliable_submission_async(
            OfferCancel(
                account=WALLET.classic_address,
                offer_sequence=OFFER.result["tx_json"]["Sequence"],
            ),
            WALLET,
            client,
        )
        self.assertTrue(response.is_successful())
        # NOTE: offer cancellations are difficult to test because not
        # specifying an offer ID to cancel is not considered an error.
        #
        # This TX will result in a success essentially as long as it is
        # correctly formatted.
