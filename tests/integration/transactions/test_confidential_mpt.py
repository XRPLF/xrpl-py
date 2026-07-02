"""Integration test for the full Confidential MPT (XLS-0096) lifecycle.

One workflow test (like test_permissioned_domain.py) exercising all five
confidential transaction types end-to-end against a standalone rippled:
convert -> merge -> send -> merge -> convert-back -> clawback, via the
high-level builders in xrpl.ext.confidential.

Runs under both the async and sync variants of @test_async_and_sync: the body
uses the async builders (prepare_confidential_*_async); the decorator's source
transform rewrites them to the sync builders, which are supplied via `modules`.

Skipped unless BOTH hold, so the suite stays green on the stock rippled image:
  * the native mpt-crypto CFFI extension is built (MPT_CRYPTO_AVAILABLE), and
  * the connected node has the ConfidentialTransfer amendment enabled.
"""

from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    JSON_RPC_CLIENT,
    fund_wallet_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from xrpl.models.amounts import MPTAmount
from xrpl.models.requests import Feature, LedgerEntry
from xrpl.models.requests.ledger_entry import MPToken as MPTokenQuery
from xrpl.models.requests.tx import Tx
from xrpl.models.transactions import (
    MPTokenAuthorize,
    MPTokenIssuanceCreate,
    MPTokenIssuanceCreateFlag,
    MPTokenIssuanceSet,
    Payment,
)
from xrpl.wallet import Wallet

try:
    from xrpl.ext.confidential import MPT_CRYPTO_AVAILABLE, MPTCrypto
    from xrpl.ext.confidential.transaction_builders import (
        prepare_confidential_clawback_async,
        prepare_confidential_convert_async,
        prepare_confidential_convert_back_async,
        prepare_confidential_merge_inbox_async,
        prepare_confidential_send_async,
    )
except ImportError:
    MPT_CRYPTO_AVAILABLE = False

# Sync counterparts for the @test_async_and_sync transform (imported into the
# generated sync test's namespace; not referenced directly, so not imported here
# to avoid F401).
_SYNC_BUILDERS = [
    "xrpl.ext.confidential.transaction_builders.prepare_confidential_convert",
    "xrpl.ext.confidential.transaction_builders.prepare_confidential_merge_inbox",
    "xrpl.ext.confidential.transaction_builders.prepare_confidential_send",
    "xrpl.ext.confidential.transaction_builders.prepare_confidential_convert_back",
    "xrpl.ext.confidential.transaction_builders.prepare_confidential_clawback",
]


def _confidential_enabled() -> bool:
    """True if mpt-crypto is built and the node has the amendment enabled."""
    if not MPT_CRYPTO_AVAILABLE:
        return False
    try:
        resp = JSON_RPC_CLIENT.request(Feature(feature="ConfidentialTransfer"))
    except Exception:
        return False
    if not resp.is_successful():
        return False
    return any(
        isinstance(v, dict)
        and v.get("name") == "ConfidentialTransfer"
        and v.get("enabled")
        for v in resp.result.values()
    )


class TestConfidentialMPT(IntegrationTestCase):
    def setUp(self):
        if not _confidential_enabled():
            self.skipTest(
                "ConfidentialTransfer amendment or mpt-crypto extension "
                "not available on this node"
            )

    def _assert_success(self, response, label):
        self.assertTrue(response.is_successful(), f"{label}: {response.result}")
        self.assertEqual(
            response.result["engine_result"],
            "tesSUCCESS",
            f"{label}: {response.result}",
        )

    @test_async_and_sync(globals(), _SYNC_BUILDERS)
    async def test_confidential_mpt_workflow(self, client):
        crypto = MPTCrypto()

        issuer = Wallet.create()
        holder1 = Wallet.create()
        holder2 = Wallet.create()
        await fund_wallet_async(issuer)
        await fund_wallet_async(holder1)
        await fund_wallet_async(holder2)

        issuer_sk, issuer_pk = crypto.generate_keypair()
        holder1_sk, holder1_pk = crypto.generate_keypair()
        holder2_sk, holder2_pk = crypto.generate_keypair()

        # Create a confidential-capable MPT issuance.
        create_res = await sign_and_reliable_submission_async(
            MPTokenIssuanceCreate(
                account=issuer.address,
                flags=(
                    MPTokenIssuanceCreateFlag.TF_MPT_CAN_LOCK
                    | MPTokenIssuanceCreateFlag.TF_MPT_CAN_CLAWBACK
                    | MPTokenIssuanceCreateFlag.TF_MPT_CAN_TRANSFER
                    | MPTokenIssuanceCreateFlag.TF_MPT_CAN_CONFIDENTIAL_AMOUNT
                ),
                maximum_amount="1000000000000",
                asset_scale=2,
            ),
            issuer,
            client,
        )
        self._assert_success(create_res, "MPTokenIssuanceCreate")
        tx_res = await client.request(
            Tx(transaction=create_res.result["tx_json"]["hash"])
        )
        mpt_id = tx_res.result["meta"]["mpt_issuance_id"]

        # Register the issuer's ElGamal key on the issuance.
        self._assert_success(
            await sign_and_reliable_submission_async(
                MPTokenIssuanceSet(
                    account=issuer.address,
                    mptoken_issuance_id=mpt_id,
                    issuer_encryption_key=issuer_pk,
                ),
                issuer,
                client,
            ),
            "MPTokenIssuanceSet (issuer key)",
        )

        # Authorize both holders.
        for holder in (holder1, holder2):
            self._assert_success(
                await sign_and_reliable_submission_async(
                    MPTokenAuthorize(
                        account=holder.address, mptoken_issuance_id=mpt_id
                    ),
                    holder,
                    client,
                ),
                "MPTokenAuthorize",
            )

        # Issue public tokens to both holders.
        self._assert_success(
            await sign_and_reliable_submission_async(
                Payment(
                    account=issuer.address,
                    destination=holder1.address,
                    amount=MPTAmount(mpt_issuance_id=mpt_id, value="10000"),
                ),
                issuer,
                client,
            ),
            "Payment -> holder1",
        )
        self._assert_success(
            await sign_and_reliable_submission_async(
                Payment(
                    account=issuer.address,
                    destination=holder2.address,
                    amount=MPTAmount(mpt_issuance_id=mpt_id, value="100"),
                ),
                issuer,
                client,
            ),
            "Payment -> holder2",
        )

        # holder1: convert public -> confidential, then merge inbox.
        convert_tx = await prepare_confidential_convert_async(
            client=client,
            wallet=holder1,
            mpt_issuance_id=mpt_id,
            amount=1000,
            holder_privkey=holder1_sk,
            holder_pubkey=holder1_pk,
            issuer_pubkey=issuer_pk,
        )
        self._assert_success(
            await sign_and_reliable_submission_async(convert_tx, holder1, client),
            "ConfidentialMPTConvert (holder1)",
        )
        merge_tx = await prepare_confidential_merge_inbox_async(
            client=client, wallet=holder1, mpt_issuance_id=mpt_id
        )
        self._assert_success(
            await sign_and_reliable_submission_async(merge_tx, holder1, client),
            "ConfidentialMPTMergeInbox (holder1)",
        )

        # holder2: convert (this also registers holder2's ElGamal key).
        convert_h2 = await prepare_confidential_convert_async(
            client=client,
            wallet=holder2,
            mpt_issuance_id=mpt_id,
            amount=100,
            holder_privkey=holder2_sk,
            holder_pubkey=holder2_pk,
            issuer_pubkey=issuer_pk,
        )
        self._assert_success(
            await sign_and_reliable_submission_async(convert_h2, holder2, client),
            "ConfidentialMPTConvert (holder2)",
        )

        # Confidential send holder1 -> holder2, then holder2 merges.
        send_tx = await prepare_confidential_send_async(
            client=client,
            sender_wallet=holder1,
            receiver_address=holder2.address,
            mpt_issuance_id=mpt_id,
            amount=300,
            sender_privkey=holder1_sk,
            sender_pubkey=holder1_pk,
            receiver_pubkey=holder2_pk,
            issuer_pubkey=issuer_pk,
        )
        self._assert_success(
            await sign_and_reliable_submission_async(send_tx, holder1, client),
            "ConfidentialMPTSend",
        )
        merge_h2 = await prepare_confidential_merge_inbox_async(
            client=client, wallet=holder2, mpt_issuance_id=mpt_id
        )
        self._assert_success(
            await sign_and_reliable_submission_async(merge_h2, holder2, client),
            "ConfidentialMPTMergeInbox (holder2)",
        )

        # holder1: convert confidential back to public.
        convert_back_tx = await prepare_confidential_convert_back_async(
            client=client,
            wallet=holder1,
            mpt_issuance_id=mpt_id,
            amount=200,
            holder_privkey=holder1_sk,
            holder_pubkey=holder1_pk,
            issuer_pubkey=issuer_pk,
        )
        self._assert_success(
            await sign_and_reliable_submission_async(convert_back_tx, holder1, client),
            "ConfidentialMPTConvertBack",
        )

        # Issuer claws back holder2's confidential balance.
        holder2_node = (
            await client.request(
                LedgerEntry(
                    mptoken=MPTokenQuery(
                        account=holder2.classic_address, mpt_issuance_id=mpt_id
                    )
                )
            )
        ).result["node"]
        issuer_encrypted_balance = holder2_node["IssuerEncryptedBalance"]
        clawback_amount = crypto.decrypt(
            issuer_sk,
            issuer_encrypted_balance[:66],
            issuer_encrypted_balance[66:132],
            0,
            100000,
        )
        self.assertGreater(clawback_amount, 0)
        clawback_tx = await prepare_confidential_clawback_async(
            client=client,
            issuer_wallet=issuer,
            holder_address=holder2.address,
            mpt_issuance_id=mpt_id,
            amount=clawback_amount,
            issuer_privkey=issuer_sk,
            issuer_pubkey=issuer_pk,
            issuer_encrypted_balance=issuer_encrypted_balance,
        )
        self._assert_success(
            await sign_and_reliable_submission_async(clawback_tx, issuer, client),
            "ConfidentialMPTClawback",
        )
