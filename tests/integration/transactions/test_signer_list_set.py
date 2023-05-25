from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import WALLET
from xrpl.models.transactions import SignerEntry, SignerListSet
from xrpl.wallet import Wallet


class TestSignerListSet(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_add_signer(self, client):
        # sets up another signer for this account
        other_signer = Wallet.create()
        response = await sign_and_reliable_submission_async(
            SignerListSet(
                account=WALLET.classic_address,
                signer_quorum=1,
                signer_entries=[
                    SignerEntry(
                        account=other_signer.classic_address,
                        signer_weight=1,
                    ),
                ],
            ),
            WALLET,
            client,
        )
        self.assertTrue(response.is_successful())
