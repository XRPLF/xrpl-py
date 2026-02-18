from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    create_mpt_token_and_authorize_source,
    create_mpt_token_and_authorize_source_async,
    fund_wallet,
    fund_wallet_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from xrpl.models.amounts import MPTAmount
from xrpl.models.requests.path_find import PathFind, PathFindSubcommand
from xrpl.models.transactions import MPTokenAuthorize, MPTokenIssuanceCreateFlag, OfferCreate
from xrpl.wallet import Wallet


class TestPathFind(IntegrationTestCase):
    @test_async_and_sync(globals(), websockets_only=True)
    async def test_path_find_with_mpt(self, client):
        issuer = Wallet.create()
        await fund_wallet_async(issuer)
        source = Wallet.create()
        await fund_wallet_async(source)
        destination = Wallet.create()
        await fund_wallet_async(destination)

        mpt_issuance_id = await create_mpt_token_and_authorize_source_async(
            issuer=issuer,
            source=source,
            client=client,
            flags=[
                MPTokenIssuanceCreateFlag.TF_MPT_CAN_TRANSFER,
                MPTokenIssuanceCreateFlag.TF_MPT_CAN_TRADE,
            ],
        )

        # Authorize destination to hold this MPT
        await sign_and_reliable_submission_async(
            MPTokenAuthorize(
                account=destination.classic_address,
                mptoken_issuance_id=mpt_issuance_id,
            ),
            destination,
            client,
        )

        # Create an offer on the DEX: source sells MPT for XRP
        await sign_and_reliable_submission_async(
            OfferCreate(
                account=source.classic_address,
                taker_gets=MPTAmount(
                    mpt_issuance_id=mpt_issuance_id,
                    value="100",
                ),
                taker_pays="1000000",
            ),
            source,
            client,
        )

        # Create the path_find request
        response = await client.request(
            PathFind(
                subcommand=PathFindSubcommand.CREATE,
                source_account=source.classic_address,
                destination_account=destination.classic_address,
                destination_amount=MPTAmount(
                    mpt_issuance_id=mpt_issuance_id,
                    value="100",
                ),
            )
        )
        self.assertTrue(response.is_successful())
        self.assertEqual(
            response.result["destination_amount"],
            {"mpt_issuance_id": mpt_issuance_id, "value": "100"},
        )
        self.assertTrue(len(response.result["alternatives"]) > 0)

        # Close the path_find subscription
        close_response = await client.request(
            PathFind(
                subcommand=PathFindSubcommand.CLOSE,
                source_account=source.classic_address,
                destination_account=destination.classic_address,
                destination_amount=MPTAmount(
                    mpt_issuance_id=mpt_issuance_id,
                    value="100",
                ),
            )
        )
        self.assertTrue(close_response.is_successful())
