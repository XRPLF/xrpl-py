from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import WALLET
from xrpl.models.mptoken_metadata import MPTokenMetadata, MPTokenMetadataUri
from xrpl.models.requests.account_objects import AccountObjects, AccountObjectType
from xrpl.models.transactions import MPTokenIssuanceCreate
from xrpl.utils.mptoken_metadata import decode_mptoken_metadata, encode_mptoken_metadata


class TestMPTokenIssuanceCreate(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):
        metadata = MPTokenMetadata(
            ticker="TBILL",
            name="T-Bill Yield Token",
            icon="https://example.org/tbill-icon.png",
            asset_class="rwa",
            asset_subclass="treasury",
            issuer_name="Example Yield Co.",
            uris=[
                MPTokenMetadataUri(
                    uri="https://exampleyield.co/tbill",
                    category="website",
                    title="Product Page",
                ),
            ],
        )

        tx = MPTokenIssuanceCreate(
            account=WALLET.classic_address,
            maximum_amount="9223372036854775807",  # "7fffffffffffffff"
            asset_scale=2,
            mptoken_metadata=encode_mptoken_metadata(metadata),
        )

        response = await sign_and_reliable_submission_async(
            tx,
            WALLET,
            client,
        )

        self.assertTrue(response.is_successful())
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # confirm MPTokenIssuance ledger object was created
        account_objects_response = await client.request(
            AccountObjects(account=WALLET.address, type=AccountObjectType.MPT_ISSUANCE)
        )

        # subsequent integration tests (sync/async + json/websocket) add one
        # MPTokenIssuance object to the account
        self.assertTrue(len(account_objects_response.result["account_objects"]) > 0)

        self.assertEqual(
            decode_mptoken_metadata(
                account_objects_response.result["account_objects"][0]["MPTokenMetadata"]
            ),
            metadata,
        )
