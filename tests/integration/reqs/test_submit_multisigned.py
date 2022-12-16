from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import sign_and_reliable_submission, test_async_and_sync
from tests.integration.reusable_values import WALLET
from xrpl.asyncio.transaction.main import autofill, sign
from xrpl.models.requests import SubmitMultisigned
from xrpl.models.transactions import AccountSet, SignerEntry, SignerListSet
from xrpl.transaction.multisign import multisign
from xrpl.utils.str_conversions import str_to_hex
from xrpl.wallet import Wallet

FIRST_SIGNER = Wallet("sEdTLQkHAWpdS7FDk7EvuS7Mz8aSMRh", 0)
SECOND_SIGNER = Wallet("sEd7DXaHkGQD8mz8xcRLDxfMLqCurif", 0)
SIGNER_ENTRIES = [
    SignerEntry(
        account=FIRST_SIGNER.classic_address,
        signer_weight=1,
    ),
    SignerEntry(
        account=SECOND_SIGNER.classic_address,
        signer_weight=1,
    ),
]
LIST_SET_TX = sign_and_reliable_submission(
    SignerListSet(
        account=WALLET.classic_address,
        signer_quorum=2,
        signer_entries=SIGNER_ENTRIES,
    ),
    WALLET,
)
EXAMPLE_DOMAIN = str_to_hex("example.com")
EXPECTED_DOMAIN = "6578616D706C652E636F6D"


class TestSubmitMultisigned(IntegrationTestCase):
    @test_async_and_sync(
        globals(),
        [
            "xrpl.transaction.sign",
            "xrpl.transaction.autofill",
        ],
    )
    async def test_basic_functionality(self, client):
        tx = AccountSet(account=WALLET.classic_address, domain=EXAMPLE_DOMAIN)

        autofilled_tx = await autofill(tx, client, len(SIGNER_ENTRIES))

        tx_1 = await sign(autofilled_tx, FIRST_SIGNER, multisign=True)
        tx_2 = await sign(autofilled_tx, SECOND_SIGNER, multisign=True)

        multisigned_tx = multisign(autofilled_tx, [tx_1, tx_2])

        # submit tx
        response = await client.request(
            SubmitMultisigned(
                tx_json=multisigned_tx,
            )
        )
        self.assertTrue(response.is_successful())
        self.assertEqual(response.result["tx_json"]["Domain"], EXPECTED_DOMAIN)
