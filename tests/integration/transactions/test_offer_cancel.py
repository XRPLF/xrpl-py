try:
    from unittest import IsolatedAsyncioTestCase
except ImportError:
    from aiounittest import AsyncTestCase as IsolatedAsyncioTestCase

from tests.integration.it_utils import submit_transaction_async, test_async_and_sync
from tests.integration.reusable_values import OFFER, WALLET
from xrpl.models.transactions import OfferCancel


class TestOfferCancel(IsolatedAsyncioTestCase):
    @test_async_and_sync(globals())
    async def test_all_fields(self, client):
        response = await submit_transaction_async(
            OfferCancel(
                account=WALLET.classic_address,
                sequence=WALLET.sequence,
                offer_sequence=OFFER.result["Sequence"],
            ),
            WALLET,
        )
        self.assertTrue(response.is_successful())
        # NOTE: offer cancellations are difficult to test because not
        # specifying an offer ID to cancel is not considered an error.
        #
        # This TX will result in a success essentially as long as it is
        # correctly formatted.
        WALLET.sequence += 1
