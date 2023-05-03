from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    LEDGER_ACCEPT_REQUEST,
    submit_transaction_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import BRIDGE, DESTINATION, WITNESS_WALLET
from xrpl.core.binarycodec import encode
from xrpl.core.keypairs import sign
from xrpl.models import (
    AccountInfo,
    Tx,
    XChainAddClaimAttestation,
    XChainClaim,
    XChainCreateClaimID,
)
from xrpl.utils import xrp_to_drops
from xrpl.wallet import Wallet


class TestXChainAddClaimAttestation(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):
        other_chain_source = Wallet.create().classic_address
        claim_id_response = await submit_transaction_async(
            XChainCreateClaimID(
                account=DESTINATION.classic_address,
                xchain_bridge=BRIDGE.xchain_bridge,
                signature_reward=BRIDGE.signature_reward,
                other_chain_source=other_chain_source,
            ),
            DESTINATION,
            client,
        )
        await client.request(LEDGER_ACCEPT_REQUEST)
        claim_id_hash = (
            claim_id_response.result.get("tx_json") or claim_id_response.result
        )["hash"]
        claim_id_tx_response = await client.request(Tx(transaction=claim_id_hash))

        nodes = claim_id_tx_response.result["meta"]["AffectedNodes"]
        created_nodes = [
            node["CreatedNode"] for node in nodes if "CreatedNode" in node.keys()
        ]
        claim_ids_ledger_entries = [
            node
            for node in created_nodes
            if node["LedgerEntryType"] == "XChainOwnedClaimID"
        ]
        assert len(claim_ids_ledger_entries) == 1, len(claim_ids_ledger_entries)
        xchain_claim_id = claim_ids_ledger_entries[0]["NewFields"]["XChainClaimID"]

        account_info1 = await client.request(
            AccountInfo(account=DESTINATION.classic_address)
        )
        initial_balance = int(account_info1.result["account_data"]["Balance"])
        amount = xrp_to_drops(300)

        attestation_to_sign = {
            "XChainBridge": BRIDGE.to_xrpl()["XChainBridge"],
            "OtherChainSource": other_chain_source,
            "Amount": amount,
            "AttestationRewardAccount": WITNESS_WALLET.classic_address,
            "WasLockingChainSend": 0,
            "XChainClaimID": xchain_claim_id,
        }
        encoded_attestation = encode(attestation_to_sign)
        attestation_signature = sign(
            bytes.fromhex(encoded_attestation),
            WITNESS_WALLET.private_key,
        )

        response = await submit_transaction_async(
            XChainAddClaimAttestation.from_xrpl(
                {
                    "Account": WITNESS_WALLET.classic_address,
                    "AttestationSignerAccount": WITNESS_WALLET.classic_address,
                    **attestation_to_sign,
                    "PublicKey": WITNESS_WALLET.public_key,
                    "Signature": attestation_signature,
                }
            ),
            WITNESS_WALLET,
            client,
        )
        self.assertTrue(response.is_successful())
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")
        await client.request(LEDGER_ACCEPT_REQUEST)

        account_info2 = await client.request(
            AccountInfo(account=DESTINATION.classic_address)
        )
        intermediate_balance = int(account_info2.result["account_data"]["Balance"])
        self.assertEqual(intermediate_balance, initial_balance)

        response = await submit_transaction_async(
            XChainClaim(
                account=DESTINATION.classic_address,
                xchain_bridge=BRIDGE.xchain_bridge,
                xchain_claim_id=xchain_claim_id,
                destination=DESTINATION.classic_address,
                amount=amount,
            ),
            DESTINATION,
            client,
        )
        self.assertTrue(response.is_successful())
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")
        await client.request(LEDGER_ACCEPT_REQUEST)

        account_info3 = await client.request(
            AccountInfo(account=DESTINATION.classic_address)
        )
        final_balance = int(account_info3.result["account_data"]["Balance"])
        self.assertEqual(
            final_balance,
            initial_balance + int(amount) - int(BRIDGE.signature_reward) - 10,
        )
