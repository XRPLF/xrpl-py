from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import sign_and_reliable_submission, test_async_and_sync
from tests.integration.reusable_values import WALLET
from xrpl.asyncio.transaction.main import autofill, sign
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.requests import SubmitMultisigned
from xrpl.models.transactions import SignerEntry, SignerListSet, TrustSet, TrustSetFlag
from xrpl.transaction.multisign import multisign
from xrpl.wallet import Wallet

# Set up signer list
FIRST_SIGNER = Wallet.create()
SECOND_SIGNER = Wallet.create()
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


class TestSubmitMultisigned(IntegrationTestCase):
    @test_async_and_sync(
        globals(),
        [
            "xrpl.transaction.sign",
            "xrpl.transaction.autofill",
        ],
    )
    async def test_basic_functionality(self, client):
        issuer = Wallet.create()
        tx = TrustSet(
            account=WALLET.classic_address,
            flags=TrustSetFlag.TF_SET_NO_RIPPLE,
            limit_amount=IssuedCurrencyAmount(
                issuer=issuer.classic_address,
                currency="USD",
                value="10",
            ),
        )
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
