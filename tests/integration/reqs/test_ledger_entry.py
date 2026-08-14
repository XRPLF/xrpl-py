from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    create_amm_pool_with_mpt_async,
    test_async_and_sync,
)
from xrpl.models.requests.ledger_entry import AMM, LedgerEntry


class TestLedgerEntry(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_ledger_entry_amm_with_mpt_assets(self, client):
        amm_pool = await create_amm_pool_with_mpt_async(client)
        mpt_asset = amm_pool["asset"]
        mpt_asset2 = amm_pool["asset2"]

        response = await client.request(
            LedgerEntry(
                amm=AMM(asset=mpt_asset, asset2=mpt_asset2),
            )
        )
        self.assertTrue(response.is_successful())

        node = response.result["node"]
        self.assertEqual(node["LedgerEntryType"], "AMM")
        self.assertEqual(
            node["Asset"],
            {"mpt_issuance_id": mpt_asset.mpt_issuance_id},
        )
        self.assertEqual(
            node["Asset2"],
            {"mpt_issuance_id": mpt_asset2.mpt_issuance_id},
        )
        self.assertEqual(node["TradingFee"], 12)
        self.assertIn("LPTokenBalance", node)
        self.assertIn("Account", node)
