"""Integration test for chaining Confidential MPT sends inside a Batch (XLS-56).

rippled applies each confidential send to the sender's ConfidentialBalance-
Spending as ``new CB_S = CB_S - SenderEncryptedAmount`` with a version bump (see
``chainAfterSend``). So a Batch containing multiple same-``(sender, token)``
confidential sends only validates if every send after the first proves against
the *predicted* state left by the previous one. ``prepare_confidential_send_batch``
threads that predicted state through the chain.

This test confirms two Batch compositions on-ledger:
  A. two chained confidential sends from one sender  (the chaining path), and
  B. one confidential send + one ordinary XRP Payment (confidential composes
     with a normal inner transaction).

Runs under both async and sync via @test_async_and_sync. Requires the
ConfidentialTransfer + BatchV1_1 amendments and the native mpt-crypto CFFI
extension (xrpl.ext.confidential).
"""

from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    fund_wallet_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from xrpl.ext.confidential import MPT_CRYPTO_AVAILABLE, MPTCrypto
from xrpl.ext.confidential.transaction_builders import (
    prepare_confidential_convert_async,
    prepare_confidential_merge_inbox_async,
    prepare_confidential_send_batch_async,
)
from xrpl.models import Batch, BatchFlag
from xrpl.models.amounts import MPTAmount
from xrpl.models.requests import LedgerEntry
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

# Sync counterparts for the @test_async_and_sync source transform (the async
# builder calls are rewritten to these; supplied via the decorator's modules).
_SYNC_BUILDERS = [
    "xrpl.ext.confidential.transaction_builders.prepare_confidential_convert",
    "xrpl.ext.confidential.transaction_builders.prepare_confidential_merge_inbox",
    "xrpl.ext.confidential.transaction_builders.prepare_confidential_send_batch",
]


class TestConfidentialMPTBatch(IntegrationTestCase):
    def setUp(self):
        if not MPT_CRYPTO_AVAILABLE:
            self.skipTest("mpt-crypto extension (xrpl.ext.confidential) not built")

    def _assert_success(self, response, label):
        self.assertTrue(response.is_successful(), f"{label}: {response.result}")
        self.assertEqual(
            response.result["engine_result"],
            "tesSUCCESS",
            f"{label}: {response.result}",
        )

    @staticmethod
    def _spending(node, crypto, privkey):
        # Synchronous so it works under both variants of @test_async_and_sync
        # (the decorator strips ``await`` in the body but not in helpers, so the
        # ledger read is done inline at the call site and only the node dict is
        # passed here).
        blob = node.get("ConfidentialBalanceSpending", "")
        if not blob:
            return 0
        return crypto.decrypt(privkey, blob[:66], blob[66:132], 0, 100000)

    @test_async_and_sync(globals(), _SYNC_BUILDERS)
    async def test_batch_confidential_send_chaining(self, client):
        crypto = MPTCrypto()

        issuer = Wallet.create()
        holder1 = Wallet.create()  # sender
        holder2 = Wallet.create()  # receiver
        holder3 = Wallet.create()  # receiver / normal-payment destination
        for w in (issuer, holder1, holder2, holder3):
            await fund_wallet_async(w)

        issuer_sk, issuer_pk = crypto.generate_keypair()
        holder1_sk, holder1_pk = crypto.generate_keypair()
        holder2_sk, holder2_pk = crypto.generate_keypair()
        holder3_sk, holder3_pk = crypto.generate_keypair()

        # Confidential-capable issuance.
        create_res = await sign_and_reliable_submission_async(
            MPTokenIssuanceCreate(
                account=issuer.address,
                flags=(
                    MPTokenIssuanceCreateFlag.TF_MPT_CAN_LOCK
                    | MPTokenIssuanceCreateFlag.TF_MPT_CAN_CLAWBACK
                    | MPTokenIssuanceCreateFlag.TF_MPT_CAN_TRANSFER
                    | MPTokenIssuanceCreateFlag.TF_MPT_CAN_HOLD_CONFIDENTIAL_BALANCE
                ),
                maximum_amount="1000000000000",
                asset_scale=2,
            ),
            issuer,
            client,
        )
        self._assert_success(create_res, "MPTokenIssuanceCreate")
        mpt_id = (
            await client.request(Tx(transaction=create_res.result["tx_json"]["hash"]))
        ).result["meta"]["mpt_issuance_id"]

        # Register the issuer's ElGamal key.
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
            "MPTokenIssuanceSet",
        )

        # Authorize holders and issue public tokens to each.
        for holder, amount in ((holder1, "10000"), (holder2, "100"), (holder3, "100")):
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
            self._assert_success(
                await sign_and_reliable_submission_async(
                    Payment(
                        account=issuer.address,
                        destination=holder.address,
                        amount=MPTAmount(mpt_issuance_id=mpt_id, value=amount),
                    ),
                    issuer,
                    client,
                ),
                f"Payment issue -> {holder.address}",
            )

        # holder1: convert 1000 public -> confidential, merge inbox -> spending=1000.
        convert = await prepare_confidential_convert_async(
            client=client,
            wallet=holder1,
            mpt_issuance_id=mpt_id,
            amount=1000,
            holder_privkey=holder1_sk,
            holder_pubkey=holder1_pk,
            issuer_pubkey=issuer_pk,
        )
        self._assert_success(
            await sign_and_reliable_submission_async(convert, holder1, client),
            "ConfidentialMPTConvert (holder1)",
        )
        merge = await prepare_confidential_merge_inbox_async(
            client=client, wallet=holder1, mpt_issuance_id=mpt_id
        )
        self._assert_success(
            await sign_and_reliable_submission_async(merge, holder1, client),
            "ConfidentialMPTMergeInbox (holder1)",
        )

        # holder2 and holder3 each convert 100 -> registers their ElGamal key so
        # they can receive, and seeds their inbox with 100.
        for holder, sk, pk in (
            (holder2, holder2_sk, holder2_pk),
            (holder3, holder3_sk, holder3_pk),
        ):
            conv = await prepare_confidential_convert_async(
                client=client,
                wallet=holder,
                mpt_issuance_id=mpt_id,
                amount=100,
                holder_privkey=sk,
                holder_pubkey=pk,
                issuer_pubkey=issuer_pk,
            )
            self._assert_success(
                await sign_and_reliable_submission_async(conv, holder, client),
                "ConfidentialMPTConvert (receiver)",
            )

        # ── Scenario A: Batch of TWO chained confidential sends ──────────────
        # holder1 -> holder2 (30) and holder1 -> holder3 (20) in one Batch. The
        # second send must bind to holder1's CB_S *after* the first applies;
        # prepare_confidential_send_batch predicts that state and pins each inner
        # send to a consecutive sequence.
        chained = await prepare_confidential_send_batch_async(
            client=client,
            sender_wallet=holder1,
            mpt_issuance_id=mpt_id,
            transfers=[
                (holder2.address, holder2_pk, 30),
                (holder3.address, holder3_pk, 20),
            ],
            sender_privkey=holder1_sk,
            sender_pubkey=holder1_pk,
            issuer_pubkey=issuer_pk,
        )
        self.assertEqual(len(chained), 2)
        batch_a = Batch(
            account=holder1.address,
            flags=BatchFlag.TF_ALL_OR_NOTHING,
            raw_transactions=list(chained),
        )
        self._assert_success(
            await sign_and_reliable_submission_async(batch_a, holder1, client),
            "Batch (2 chained confidential sends)",
        )

        # holder1 spent 30 + 20 -> 950 remaining.
        holder1_node = (
            await client.request(
                LedgerEntry(
                    mptoken=MPTokenQuery(
                        account=holder1.classic_address, mpt_issuance_id=mpt_id
                    )
                )
            )
        ).result["node"]
        self.assertEqual(
            self._spending(holder1_node, crypto, holder1_sk),
            950,
            "holder1 spending after chained batch",
        )
        # Receivers merge their inboxes: holder2 = 100 + 30, holder3 = 100 + 20.
        for holder, sk, expected in (
            (holder2, holder2_sk, 130),
            (holder3, holder3_sk, 120),
        ):
            m = await prepare_confidential_merge_inbox_async(
                client=client, wallet=holder, mpt_issuance_id=mpt_id
            )
            self._assert_success(
                await sign_and_reliable_submission_async(m, holder, client),
                "ConfidentialMPTMergeInbox (receiver)",
            )
            node = (
                await client.request(
                    LedgerEntry(
                        mptoken=MPTokenQuery(
                            account=holder.classic_address, mpt_issuance_id=mpt_id
                        )
                    )
                )
            ).result["node"]
            self.assertEqual(
                self._spending(node, crypto, sk),
                expected,
                "receiver spending after chained batch + merge",
            )

        # ── Scenario B: Batch of ONE confidential send + ONE ordinary Payment ─
        # A single confidential send (holder1 -> holder2, 40) composed with a
        # normal XRP Payment (holder1 -> holder3). The confidential inner is
        # pinned by the builder; the Payment must be pinned to the next sequence
        # so it does not collide (batch autofill only advances its counter for
        # inners it assigns itself).
        one_send = await prepare_confidential_send_batch_async(
            client=client,
            sender_wallet=holder1,
            mpt_issuance_id=mpt_id,
            transfers=[(holder2.address, holder2_pk, 40)],
            sender_privkey=holder1_sk,
            sender_pubkey=holder1_pk,
            issuer_pubkey=issuer_pk,
        )
        self.assertEqual(len(one_send), 1)
        payment = Payment(
            account=holder1.address,
            destination=holder3.address,
            amount="1",
            sequence=one_send[0].sequence + 1,
        )
        batch_b = Batch(
            account=holder1.address,
            flags=BatchFlag.TF_ALL_OR_NOTHING,
            raw_transactions=[one_send[0], payment],
        )
        self._assert_success(
            await sign_and_reliable_submission_async(batch_b, holder1, client),
            "Batch (confidential send + normal Payment)",
        )

        # holder1 spent another 40 -> 910.
        holder1_node = (
            await client.request(
                LedgerEntry(
                    mptoken=MPTokenQuery(
                        account=holder1.classic_address, mpt_issuance_id=mpt_id
                    )
                )
            )
        ).result["node"]
        self.assertEqual(
            self._spending(holder1_node, crypto, holder1_sk),
            910,
            "holder1 spending after mixed batch",
        )
        # holder2 receives 40 into its inbox; merge -> 130 + 40 = 170.
        m2 = await prepare_confidential_merge_inbox_async(
            client=client, wallet=holder2, mpt_issuance_id=mpt_id
        )
        self._assert_success(
            await sign_and_reliable_submission_async(m2, holder2, client),
            "ConfidentialMPTMergeInbox (holder2, scenario B)",
        )
        holder2_node = (
            await client.request(
                LedgerEntry(
                    mptoken=MPTokenQuery(
                        account=holder2.classic_address, mpt_issuance_id=mpt_id
                    )
                )
            )
        ).result["node"]
        self.assertEqual(
            self._spending(holder2_node, crypto, holder2_sk),
            170,
            "holder2 spending after mixed batch + merge",
        )
