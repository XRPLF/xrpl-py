"""Integration test for the full Confidential MPT (XLS-0096) lifecycle.

One workflow test (like test_permissioned_domain.py) exercising all five
confidential transaction types end-to-end against a standalone rippled:
convert -> merge -> send -> merge -> convert-back -> clawback, via the
high-level builders in xrpl.ext.confidential.

Runs under both the async and sync variants of @test_async_and_sync: the body
uses the async builders (prepare_confidential_*_async); the decorator's source
transform rewrites them to the sync builders, which are supplied via `modules`.

Requires the ConfidentialTransfer amendment on the connected node and the native
mpt-crypto CFFI extension (xrpl.ext.confidential) to be built.
"""

from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    fund_wallet_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from xrpl.ext.confidential import MPT_CRYPTO_AVAILABLE, MPTCrypto
from xrpl.ext.confidential.transaction_builders import (
    prepare_confidential_clawback_async,
    prepare_confidential_convert_async,
    prepare_confidential_convert_back_async,
    prepare_confidential_merge_inbox_async,
    prepare_confidential_send_async,
)
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


class TestConfidentialMPT(IntegrationTestCase):
    def setUp(self):
        # The native mpt-crypto CFFI extension ships as the separate
        # xrpl-py-confidential distribution and is not built in core CI; skip
        # cleanly when it is absent (same pattern as the native unit tests).
        if not MPT_CRYPTO_AVAILABLE:
            self.skipTest("mpt-crypto extension (xrpl.ext.confidential) not built")

    def _assert_success(self, response, label):
        self.assertTrue(response.is_successful(), f"{label}: {response.result}")
        self.assertEqual(
            response.result["engine_result"],
            "tesSUCCESS",
            f"{label}: {response.result}",
        )

    async def _decrypt_balance(
        self, client, crypto, account, mpt_id, privkey, field, range_high=100000
    ):
        """Decrypt an ElGamal balance blob (c1||c2) on the holder's MPToken.

        ``field`` is a balance SField such as ConfidentialBalanceSpending,
        ConfidentialBalanceInbox, IssuerEncryptedBalance or
        AuditorEncryptedBalance. Returns 0 when the field is absent.
        """
        node = (
            await client.request(
                LedgerEntry(
                    mptoken=MPTokenQuery(account=account, mpt_issuance_id=mpt_id)
                )
            )
        ).result["node"]
        blob = node.get(field, "")
        if not blob:
            return 0
        return crypto.decrypt(privkey, blob[:66], blob[66:132], 0, range_high)

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
        # Auditor key: once registered on the issuance, every confidential
        # transaction must carry an auditor ciphertext, so it is threaded through
        # all builders below and its mirror balance is asserted at the end.
        auditor_sk, auditor_pk = crypto.generate_keypair()

        # Create a confidential-capable MPT issuance.
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
        tx_res = await client.request(
            Tx(transaction=create_res.result["tx_json"]["hash"])
        )
        mpt_id = tx_res.result["meta"]["mpt_issuance_id"]

        # Register the issuer's and auditor's ElGamal keys on the issuance.
        self._assert_success(
            await sign_and_reliable_submission_async(
                MPTokenIssuanceSet(
                    account=issuer.address,
                    mptoken_issuance_id=mpt_id,
                    issuer_encryption_key=issuer_pk,
                    auditor_encryption_key=auditor_pk,
                ),
                issuer,
                client,
            ),
            "MPTokenIssuanceSet (issuer + auditor keys)",
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
            auditor_pubkey=auditor_pk,
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
        # After converting 1000 and merging the inbox, holder1's decrypted
        # spending balance must be exactly 1000.
        self.assertEqual(
            await self._decrypt_balance(
                client,
                crypto,
                holder1.classic_address,
                mpt_id,
                holder1_sk,
                "ConfidentialBalanceSpending",
            ),
            1000,
            "holder1 spending balance after convert+merge",
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
            auditor_pubkey=auditor_pk,
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
            auditor_pubkey=auditor_pk,
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
        # holder1 sent 300 of its 1000 -> 700 remaining. holder2 converted 100
        # then received 300 and merged -> 400. Confirm both by decryption.
        self.assertEqual(
            await self._decrypt_balance(
                client,
                crypto,
                holder1.classic_address,
                mpt_id,
                holder1_sk,
                "ConfidentialBalanceSpending",
            ),
            700,
            "holder1 spending balance after send",
        )
        self.assertEqual(
            await self._decrypt_balance(
                client,
                crypto,
                holder2.classic_address,
                mpt_id,
                holder2_sk,
                "ConfidentialBalanceSpending",
            ),
            400,
            "holder2 spending balance after receiving send",
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
            auditor_pubkey=auditor_pk,
        )
        self._assert_success(
            await sign_and_reliable_submission_async(convert_back_tx, holder1, client),
            "ConfidentialMPTConvertBack",
        )
        # holder1 converted 200 back to public -> 500 confidential remaining.
        self.assertEqual(
            await self._decrypt_balance(
                client,
                crypto,
                holder1.classic_address,
                mpt_id,
                holder1_sk,
                "ConfidentialBalanceSpending",
            ),
            500,
            "holder1 spending balance after convert-back",
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
        # The issuer mirror tracks holder2's confidential balance (400), and the
        # auditor mirror must track the same amount.
        self.assertEqual(clawback_amount, 400, "issuer mirror of holder2 balance")
        self.assertEqual(
            await self._decrypt_balance(
                client,
                crypto,
                holder2.classic_address,
                mpt_id,
                auditor_sk,
                "AuditorEncryptedBalance",
            ),
            400,
            "auditor mirror of holder2 balance",
        )
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
        # Clawback reclaimed the full balance -> holder2 spending balance is 0.
        self.assertEqual(
            await self._decrypt_balance(
                client,
                crypto,
                holder2.classic_address,
                mpt_id,
                holder2_sk,
                "ConfidentialBalanceSpending",
            ),
            0,
            "holder2 spending balance after clawback",
        )
