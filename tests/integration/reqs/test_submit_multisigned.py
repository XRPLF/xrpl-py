from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    JSON_RPC_CLIENT,
    sign_and_reliable_submission,
    test_async_and_sync,
)
from tests.integration.reusable_values import WALLET
from xrpl.asyncio.clients.utils import (
    json_to_response,
    request_to_json_rpc,
    request_to_websocket,
    websocket_to_response,
)
from xrpl.core.binarycodec import encode_for_multisigning
from xrpl.core.keypairs import sign
from xrpl.ledger import get_fee
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.requests import SubmitMultisigned
from xrpl.models.transactions import (
    Signer,
    SignerEntry,
    SignerListSet,
    TrustSet,
    TrustSetFlag,
)
from xrpl.wallet import Wallet

FEE = get_fee(JSON_RPC_CLIENT)

#
# Set up signer list
FIRST_SIGNER = Wallet.create()
SECOND_SIGNER = Wallet.create()
LIST_SET_TX = sign_and_reliable_submission(
    SignerListSet(
        account=WALLET.classic_address,
        sequence=WALLET.sequence,
        last_ledger_sequence=WALLET.sequence + 10,
        fee=FEE,
        signer_quorum=2,
        signer_entries=[
            SignerEntry(
                account=FIRST_SIGNER.classic_address,
                signer_weight=1,
            ),
            SignerEntry(
                account=SECOND_SIGNER.classic_address,
                signer_weight=1,
            ),
        ],
    ),
    WALLET,
)


class TestSubmitMultisigned(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):
        #
        # Perform multisign
        #
        # NOTE: If you need to use xrpl-py for multisigning, please create an issue on
        # the repo. We'd like to gauge interest in higher level multisigning
        # functionality.
        issuer = Wallet.create()
        tx = TrustSet(
            account=WALLET.classic_address,
            sequence=WALLET.sequence,
            fee=FEE,
            flags=TrustSetFlag.TF_SET_NO_RIPPLE,
            limit_amount=IssuedCurrencyAmount(
                issuer=issuer.classic_address,
                currency="USD",
                value="10",
            ),
        )
        tx_json = tx.to_xrpl()
        first_sig = sign(
            bytes.fromhex(
                encode_for_multisigning(
                    tx_json,
                    FIRST_SIGNER.classic_address,
                )
            ),
            FIRST_SIGNER.private_key,
        )
        second_sig = sign(
            bytes.fromhex(
                encode_for_multisigning(
                    tx_json,
                    SECOND_SIGNER.classic_address,
                )
            ),
            SECOND_SIGNER.private_key,
        )
        multisigned_tx = TrustSet(
            account=WALLET.classic_address,
            sequence=WALLET.sequence,
            fee=FEE,
            flags=TrustSetFlag.TF_SET_NO_RIPPLE,
            limit_amount=IssuedCurrencyAmount(
                issuer=issuer.classic_address,
                currency="USD",
                value="10",
            ),
            signers=[
                Signer(
                    account=FIRST_SIGNER.classic_address,
                    txn_signature=first_sig,
                    signing_pub_key=FIRST_SIGNER.public_key,
                ),
                Signer(
                    account=SECOND_SIGNER.classic_address,
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

    @test_async_and_sync(globals())
    async def test_request_json(self, client):
        # TODO: run request_json tests via metaprogramming, instead of copy-paste
        issuer = Wallet.create()
        tx = TrustSet(
            account=WALLET.classic_address,
            sequence=WALLET.sequence,
            fee=FEE,
            flags=TrustSetFlag.TF_SET_NO_RIPPLE,
            limit_amount=IssuedCurrencyAmount(
                issuer=issuer.classic_address,
                currency="USD",
                value="10",
            ),
        )
        tx_json = tx.to_xrpl()
        first_sig = sign(
            bytes.fromhex(
                encode_for_multisigning(
                    tx_json,
                    FIRST_SIGNER.classic_address,
                )
            ),
            FIRST_SIGNER.private_key,
        )
        second_sig = sign(
            bytes.fromhex(
                encode_for_multisigning(
                    tx_json,
                    SECOND_SIGNER.classic_address,
                )
            ),
            SECOND_SIGNER.private_key,
        )
        multisigned_tx = TrustSet(
            account=WALLET.classic_address,
            sequence=WALLET.sequence,
            fee=FEE,
            flags=TrustSetFlag.TF_SET_NO_RIPPLE,
            limit_amount=IssuedCurrencyAmount(
                issuer=issuer.classic_address,
                currency="USD",
                value="10",
            ),
            signers=[
                Signer(
                    account=FIRST_SIGNER.classic_address,
                    txn_signature=first_sig,
                    signing_pub_key=FIRST_SIGNER.public_key,
                ),
                Signer(
                    account=SECOND_SIGNER.classic_address,
                    txn_signature=second_sig,
                    signing_pub_key=SECOND_SIGNER.public_key,
                ),
            ],
        )

        is_websocket = "ws" in client.url
        req = SubmitMultisigned(
            tx_json=multisigned_tx,
        )
        if is_websocket:
            request = request_to_websocket(req)
        else:
            request = request_to_json_rpc(req)
        response = await client.request_json(request)
        if is_websocket:
            resp = websocket_to_response(response)
        else:
            resp = json_to_response(response)
        self.assertTrue(resp.is_successful())
