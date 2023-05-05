from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import BRIDGE, WITNESS_WALLET
from xrpl.asyncio.account import does_account_exist
from xrpl.core.binarycodec import encode
from xrpl.core.keypairs import sign
from xrpl.models import (
    AccountObjects,
    AccountObjectType,
    XChainAddAccountCreateAttestation,
)
from xrpl.utils import xrp_to_drops
from xrpl.wallet import Wallet


class TestXChainAddAccountCreateAttestation(IntegrationTestCase):
    @test_async_and_sync(globals(), ["xrpl.account.does_account_exist"])
    async def test_basic_functionality(self, client):
        destination = Wallet.create().classic_address
        other_chain_source = Wallet.create().classic_address
        self.assertFalse(await does_account_exist(destination, client))

        account_objects = await client.request(
            AccountObjects(
                account=BRIDGE.xchain_bridge.locking_chain_door,
                type=AccountObjectType.BRIDGE,
            )
        )
        bridge_obj = account_objects.result["account_objects"][0]

        attestation_to_sign = {
            "XChainBridge": BRIDGE.to_xrpl()["XChainBridge"],
            "OtherChainSource": other_chain_source,
            "Amount": xrp_to_drops(300),
            "AttestationRewardAccount": WITNESS_WALLET.classic_address,
            "WasLockingChainSend": 0,
            "XChainAccountCreateCount": int(bridge_obj["XChainAccountClaimCount"]) + 1,
            "Destination": destination,
            "SignatureReward": BRIDGE.signature_reward,
        }
        encoded_attestation = encode(attestation_to_sign)
        attestation_signature = sign(
            bytes.fromhex(encoded_attestation),
            WITNESS_WALLET.private_key,
        )

        response = await sign_and_reliable_submission_async(
            XChainAddAccountCreateAttestation.from_xrpl(
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

        self.assertTrue(await does_account_exist(destination, client))
