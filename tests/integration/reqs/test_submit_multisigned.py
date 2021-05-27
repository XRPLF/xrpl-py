try:
    from unittest import IsolatedAsyncioTestCase
except ImportError:
    from aiounittest import AsyncTestCase as IsolatedAsyncioTestCase

from tests.integration.it_utils import (
    JSON_RPC_CLIENT,
    sign_and_reliable_submission,
    test_async_and_sync,
)
from tests.integration.reusable_values import WALLET
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
from xrpl.transaction import transaction_json_to_binary_codec_form
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


class TestSubmitMultisigned(IsolatedAsyncioTestCase):
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
        tx_json = transaction_json_to_binary_codec_form(tx.to_dict())
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
                tx_json=transaction_json_to_binary_codec_form(multisigned_tx.to_dict()),
            )
        )
        self.assertTrue(response.is_successful())
