from deepdiff import DeepDiff

from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import sign_and_reliable_submission, test_async_and_sync
from tests.integration.reusable_values import WALLET
from xrpl.asyncio.transaction.main import autofill, sign
from xrpl.models.requests import SubmitMultisigned
from xrpl.models.transactions import AccountSet, SignerEntry, SignerListSet
from xrpl.transaction.multisign import multisign
from xrpl.utils.str_conversions import str_to_hex
from xrpl.wallet import Wallet

# Set up signer list
FIRST_SIGNER = Wallet("sEd7DXaHkGQD8mz8xcRLDxfMLqCurif", 0)
SECOND_SIGNER = Wallet("sEdTLQkHAWpdS7FDk7EvuS7Mz8aSMRh", 0)
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
        tx = AccountSet(
            account=WALLET.classic_address, domain=str_to_hex("example.com")
        )

        autofilled_tx = await autofill(tx, client, len(SIGNER_ENTRIES))
        expected_autofilled_tx = {
            "Account": WALLET.classic_address,
            "TransactionType": "AccountSet",
            "Fee": "40",
            "Sequence": autofilled_tx.sequence,
            "Flags": 0,
            "LastLedgerSequence": autofilled_tx.last_ledger_sequence,
            "SigningPubKey": "",
            "Domain": "6578616d706c652e636f6d",
        }
        self.assertEqual(autofilled_tx.to_xrpl(), expected_autofilled_tx)

        tx_1 = await sign(autofilled_tx, FIRST_SIGNER, multisign=True)
        signer_1_data = {
            "Signer": {
                "Account": FIRST_SIGNER.classic_address,
                "SigningPubKey": FIRST_SIGNER.public_key,
                "TxnSignature": tx_1.signers[0].txn_signature,
            }
        }
        expected_tx_1 = {**expected_autofilled_tx, "Signers": [signer_1_data]}
        self.assertEqual(tx_1.to_xrpl(), expected_tx_1)

        tx_2 = await sign(autofilled_tx, SECOND_SIGNER, multisign=True)
        signer_2_data = {
            "Signer": {
                "Account": SECOND_SIGNER.classic_address,
                "SigningPubKey": SECOND_SIGNER.public_key,
                "TxnSignature": tx_2.signers[0].txn_signature,
            }
        }
        expected_tx_2 = {**expected_autofilled_tx, "Signers": [signer_2_data]}
        self.assertEqual(tx_2.to_xrpl(), expected_tx_2)

        multisigned_tx = multisign(autofilled_tx, [tx_1, tx_2])
        expected_multisigned_tx = {
            **expected_autofilled_tx,
            "Signers": [signer_1_data, signer_2_data],
        }
        self.assertEqual(multisigned_tx.to_xrpl(), expected_multisigned_tx)

        # submit tx
        response = await client.request(
            SubmitMultisigned(
                tx_json=multisigned_tx,
            )
        )
        self.assertTrue(response.is_successful())

        # encoding to blob and hashing weirdly because of order?
        expected_response = {
            "status": "success",
            "type": "response",
            "result": {
                "engine_result": "tesSUCCESS",
                "engine_result_code": 0,
                "engine_result_message": "The transaction was applied. "
                "Only final in a validated ledger.",
                # "tx_blob": encode(multisigned_tx.to_xrpl()),
                "tx_blob": response.result["tx_blob"],
                "tx_json": {
                    **multisigned_tx.to_xrpl(),
                    # "hash": multisigned_tx.get_hash(),
                    "hash": response.result["tx_json"]["hash"],
                },
            },
        }
        if response.id is not None:
            expected_response["id"] = response.id

        self.assertEqual(
            DeepDiff(
                response.to_dict(),
                expected_response,
                ignore_order=True,
                ignore_string_case=True,
            ),
            {},
        )
