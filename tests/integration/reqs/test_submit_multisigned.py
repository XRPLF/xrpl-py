from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    JSON_RPC_CLIENT,
    sign_and_reliable_submission,
    test_async_and_sync,
)
from tests.integration.reusable_values import WALLET
from xrpl.asyncio.account import get_next_valid_seq_number
from xrpl.asyncio.transaction.main import autofill, sign
from xrpl.core.binarycodec import encode_for_multisigning
from xrpl.core.keypairs import sign as byte_sign
from xrpl.ledger import get_fee
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.requests import SubmitMultisigned
from xrpl.models.transactions import AccountSet, SignerEntry, SignerListSet
from xrpl.models.transactions.transaction import Signer
from xrpl.models.transactions.trust_set import TrustSet, TrustSetFlag
from xrpl.transaction.multisign import multisign
from xrpl.utils.str_conversions import str_to_hex
from xrpl.wallet import Wallet

FEE = get_fee(JSON_RPC_CLIENT)

# Set up signer list
FIRST_SIGNER = Wallet.create()
SECOND_SIGNER = Wallet.create()
SIGNER_ENTRIES = [
    SignerEntry(
        account=FIRST_SIGNER.address,
        signer_weight=1,
    ),
    SignerEntry(
        account=SECOND_SIGNER.address,
        signer_weight=1,
    ),
]
LIST_SET_TX = sign_and_reliable_submission(
    SignerListSet(
        account=WALLET.address,
        signer_quorum=2,
        signer_entries=SIGNER_ENTRIES,
    ),
    WALLET,
)
EXAMPLE_DOMAIN = str_to_hex("example.com")
EXPECTED_DOMAIN = "6578616D706C652E636F6D"


class TestSubmitMultisigned(IntegrationTestCase):
    @test_async_and_sync(globals(), ["xrpl.account.get_next_valid_seq_number"])
    async def test_basic_functionality(self, client):
        #
        # Perform multisign
        #
        # NOTE: If you need to use xrpl-py for multisigning, please create an issue on
        # the repo. We'd like to gauge interest in higher level multisigning
        # functionality.
        issuer = Wallet.create()
        tx = TrustSet(
            account=WALLET.address,
            sequence=await get_next_valid_seq_number(WALLET.address, client),
            fee=FEE,
            flags=TrustSetFlag.TF_SET_NO_RIPPLE,
            limit_amount=IssuedCurrencyAmount(
                issuer=issuer.address,
                currency="USD",
                value="10",
            ),
        )
        tx_json = tx.to_xrpl()
        first_sig = byte_sign(
            bytes.fromhex(
                encode_for_multisigning(
                    tx_json,
                    FIRST_SIGNER.address,
                )
            ),
            FIRST_SIGNER.private_key,
        )
        second_sig = byte_sign(
            bytes.fromhex(
                encode_for_multisigning(
                    tx_json,
                    SECOND_SIGNER.address,
                )
            ),
            SECOND_SIGNER.private_key,
        )
        multisigned_tx = TrustSet(
            account=WALLET.address,
            sequence=await get_next_valid_seq_number(WALLET.address, client),
            fee=FEE,
            flags=TrustSetFlag.TF_SET_NO_RIPPLE,
            limit_amount=IssuedCurrencyAmount(
                issuer=issuer.address,
                currency="USD",
                value="10",
            ),
            signers=[
                Signer(
                    account=FIRST_SIGNER.address,
                    txn_signature=first_sig,
                    signing_pub_key=FIRST_SIGNER.public_key,
                ),
                Signer(
                    account=SECOND_SIGNER.address,
                    txn_signature=second_sig,
                    signing_pub_key=SECOND_SIGNER.public_key,
                ),
            ],
        )

        # submit tx
        response = await client.request(
            SubmitMultisigned(
                tx_json=multisigned_tx,
            )
        )
        self.assertTrue(response.is_successful())

    @test_async_and_sync(
        globals(),
        [
            "xrpl.transaction.sign",
            "xrpl.transaction.autofill",
        ],
    )
    async def test_multisign_helper_functionality(self, client):
        tx = AccountSet(account=WALLET.address, domain=EXAMPLE_DOMAIN)

        autofilled_tx = await autofill(tx, client, len(SIGNER_ENTRIES))

        tx_1 = sign(autofilled_tx, FIRST_SIGNER, multisign=True)
        tx_2 = sign(autofilled_tx, SECOND_SIGNER, multisign=True)

        multisigned_tx = multisign(autofilled_tx, [tx_1, tx_2])

        # submit tx
        response = await client.request(
            SubmitMultisigned(
                tx_json=multisigned_tx,
            )
        )
        self.assertTrue(response.is_successful())
        self.assertEqual(response.result["tx_json"]["Domain"], EXPECTED_DOMAIN)
