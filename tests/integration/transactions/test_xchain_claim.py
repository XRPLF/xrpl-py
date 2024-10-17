from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import BRIDGE, DESTINATION, WITNESS_WALLET
from xrpl.asyncio.ledger import get_fee
from xrpl.core.binarycodec import encode
from xrpl.core.keypairs import sign
from xrpl.models import (
    AccountInfo,
    Tx,
    XChainAddClaimAttestation,
    XChainClaim,
    XChainCreateClaimID,
)
from xrpl.utils import get_xchain_claim_id, xrp_to_drops
from xrpl.wallet import Wallet


class TestXChainClaim(IntegrationTestCase):
    @test_async_and_sync(globals(), ["xrpl.ledger.get_fee"])
    async def test_basic_functionality(self, client):
        other_chain_source = Wallet.create().classic_address
        claim_id_response = await sign_and_reliable_submission_async(
            XChainCreateClaimID(
                account=DESTINATION.classic_address,
                xchain_bridge=BRIDGE.xchain_bridge,
                signature_reward=BRIDGE.signature_reward,
                other_chain_source=other_chain_source,
            ),
            DESTINATION,
            client,
        )
        claim_id_hash = (
            claim_id_response.result.get("tx_json") or claim_id_response.result
        )["hash"]
        claim_id_tx_response = await client.request(Tx(transaction=claim_id_hash))
        xchain_claim_id = get_xchain_claim_id(claim_id_tx_response.result["meta"])

        account_info1 = await client.request(
            AccountInfo(account=DESTINATION.classic_address)
        )
        initial_balance = int(account_info1.result["account_data"]["Balance"])
        amount = xrp_to_drops(3)

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

        response = await sign_and_reliable_submission_async(
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

        account_info2 = await client.request(
            AccountInfo(account=DESTINATION.classic_address)
        )
        intermediate_balance = int(account_info2.result["account_data"]["Balance"])
        self.assertEqual(intermediate_balance, initial_balance)

        response = await sign_and_reliable_submission_async(
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

        account_info3 = await client.request(
            AccountInfo(account=DESTINATION.classic_address)
        )
        final_balance = int(account_info3.result["account_data"]["Balance"])
        transaction_fee = int(await get_fee(client))
        self.assertEqual(
            final_balance,
            initial_balance
            + int(amount)
            - int(BRIDGE.signature_reward)
            - transaction_fee,
        )
