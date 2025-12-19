from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    fund_wallet_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from xrpl.models.requests import LedgerEntry
from xrpl.models.requests.ledger_entry import Directory
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import DIDSet
from xrpl.wallet import Wallet

_VALID_FIELD = "1234567890abcdefABCDEF"


class TestLedgerEntry(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_fetch_directory_model(self, client):

        owner_wallet = Wallet.create()
        await fund_wallet_async(owner_wallet)

        # Create DID ledger object to populate the directory of owner_wallet account
        setup_tx = DIDSet(
            account=owner_wallet.address,
            did_document=_VALID_FIELD,
            uri=_VALID_FIELD,
            data=_VALID_FIELD,
        )
        response = await sign_and_reliable_submission_async(
            setup_tx, owner_wallet, client
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # fetch the directory using the Dataclass model
        response = await client.request(
            LedgerEntry(directory=Directory(owner=owner_wallet.address, sub_index=0))
        )
        self.assertTrue(response.is_successful())
        self.assertEqual(response.result["node"]["LedgerEntryType"], "DirectoryNode")

        DIR_NODE_INDEX = response.result["index"]

        # fetch directory using JSON input
        response = await client.request(
            LedgerEntry(
                directory={
                    "owner": owner_wallet.address,
                    "sub_index": 0,
                },
            )
        )
        self.assertTrue(response.is_successful())
        self.assertEqual(response.result["node"]["LedgerEntryType"], "DirectoryNode")

        # fetch directory using the ledger index
        response = await client.request(LedgerEntry(index=DIR_NODE_INDEX))
        self.assertTrue(response.is_successful())
        self.assertEqual(response.result["node"]["LedgerEntryType"], "DirectoryNode")
