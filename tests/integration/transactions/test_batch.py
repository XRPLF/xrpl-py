from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    fund_wallet_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import DESTINATION, WALLET
from xrpl.asyncio.transaction import autofill
from xrpl.models import (
    Batch,
    BatchFlag,
    CheckCreate,
    DelegateSet,
    Payment,
    SignerEntry,
    SignerListSet,
    TicketCreate,
)
from xrpl.models.requests.account_objects import AccountObjects, AccountObjectType
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions.delegate_set import Permission
from xrpl.models.transactions.sponsor_signature import SponsorSignature
from xrpl.models.transactions.types import TransactionType
from xrpl.transaction.batch_signers import (
    combine_batch_signers,
    sign_multiaccount_batch,
)
from xrpl.transaction.sponsor_signer import sign_as_sponsor
from xrpl.wallet import Wallet


class TestBatch(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_all_or_nothing(self, client):
        payment = Payment(
            account=WALLET.address,
            amount="1",
            destination=DESTINATION.address,
        )
        batch = Batch(
            account=WALLET.address,
            flags=BatchFlag.TF_ALL_OR_NOTHING,
            raw_transactions=[payment, payment],
        )
        response = await sign_and_reliable_submission_async(batch, WALLET, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

    @test_async_and_sync(globals())
    async def test_independent(self, client):
        payment = Payment(
            account=WALLET.address,
            amount="1",
            destination=DESTINATION.address,
        )
        batch = Batch(
            account=WALLET.address,
            flags=BatchFlag.TF_INDEPENDENT,
            raw_transactions=[payment, payment],
        )
        response = await sign_and_reliable_submission_async(batch, WALLET, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

    @test_async_and_sync(globals(), ["xrpl.transaction.autofill"])
    async def test_multi_account_single_sign(self, client):
        payment = Payment(
            account=WALLET.address,
            amount="1",
            destination=DESTINATION.address,
        )
        payment2 = Payment(
            account=DESTINATION.address,
            amount="1",
            destination=WALLET.address,
        )
        batch = Batch(
            account=WALLET.address,
            flags=BatchFlag.TF_ALL_OR_NOTHING,
            raw_transactions=[payment, payment2],
        )
        autofilled = await autofill(batch, client, 1)
        signed = sign_multiaccount_batch(DESTINATION, autofilled)
        response = await sign_and_reliable_submission_async(signed, WALLET, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

    @test_async_and_sync(globals(), ["xrpl.transaction.autofill"])
    async def test_combine_batch_signers(self, client):
        signer = Wallet.create()
        await fund_wallet_async(signer)
        batch = Batch(
            account=WALLET.address,
            flags=BatchFlag.TF_ALL_OR_NOTHING,
            raw_transactions=[
                Payment(
                    account=WALLET.address,
                    amount="1",
                    destination=DESTINATION.address,
                ),
                Payment(
                    account=DESTINATION.address,
                    amount="1",
                    destination=WALLET.address,
                ),
                Payment(
                    account=signer.address,
                    amount="1",
                    destination=WALLET.address,
                ),
            ],
        )
        autofilled = await autofill(batch, client, 2)
        signed_dest = sign_multiaccount_batch(DESTINATION, autofilled)
        signed_signer = sign_multiaccount_batch(signer, autofilled)
        combined = Batch.from_blob(combine_batch_signers([signed_dest, signed_signer]))
        response = await sign_and_reliable_submission_async(combined, WALLET, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

    @test_async_and_sync(globals(), ["xrpl.transaction.autofill"])
    async def test_ticket_sequence(self, client):
        # The V1_1 signing payload binds the outer sequence value, which is the
        # TicketSequence when a ticket is used. This exercises that path.
        await sign_and_reliable_submission_async(
            TicketCreate(account=WALLET.address, ticket_count=1), WALLET, client
        )
        ticket_objects = await client.request(
            AccountObjects(account=WALLET.address, type=AccountObjectType.TICKET)
        )
        ticket_sequence = max(
            obj["TicketSequence"] for obj in ticket_objects.result["account_objects"]
        )

        batch = Batch(
            account=WALLET.address,
            flags=BatchFlag.TF_ALL_OR_NOTHING,
            sequence=0,
            ticket_sequence=ticket_sequence,
            raw_transactions=[
                Payment(
                    account=WALLET.address,
                    amount="1",
                    destination=DESTINATION.address,
                ),
                Payment(
                    account=DESTINATION.address,
                    amount="1",
                    destination=WALLET.address,
                ),
            ],
        )
        autofilled = await autofill(batch, client, 1)
        signed = sign_multiaccount_batch(DESTINATION, autofilled)
        response = await sign_and_reliable_submission_async(signed, WALLET, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

    @test_async_and_sync(globals(), ["xrpl.transaction.autofill"])
    async def test_delegated_inner_transaction(self, client):
        # A delegated inner transaction is authorized by its delegate, so the
        # delegate (not the account holder) provides the BatchSigner.
        alice = Wallet.create()
        await fund_wallet_async(alice)
        bob = Wallet.create()
        await fund_wallet_async(bob)

        # Authorize bob to submit Payment transactions on alice's behalf.
        await sign_and_reliable_submission_async(
            DelegateSet(
                account=alice.address,
                authorize=bob.address,
                permissions=[Permission(permission_value=TransactionType.PAYMENT)],
            ),
            alice,
            client,
            check_fee=False,
        )

        batch = Batch(
            account=WALLET.address,
            flags=BatchFlag.TF_ALL_OR_NOTHING,
            raw_transactions=[
                Payment(
                    account=WALLET.address,
                    amount="1",
                    destination=alice.address,
                ),
                Payment(
                    account=alice.address,
                    delegate=bob.address,
                    amount="1",
                    destination=WALLET.address,
                ),
            ],
        )
        autofilled = await autofill(batch, client, 1)
        signed = sign_multiaccount_batch(bob, autofilled, batch_account=bob.address)
        self.assertIsNotNone(signed.batch_signers)
        self.assertEqual(signed.batch_signers[0].account, bob.address)
        response = await sign_and_reliable_submission_async(signed, WALLET, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

    @test_async_and_sync(globals(), ["xrpl.transaction.autofill"])
    async def test_multi_account_multi_sign(self, client):
        # A multisig batch account's members sign separately, so combine must
        # merge their fragments into one BatchSigner with both inner signers.
        alice = Wallet.create()
        await fund_wallet_async(alice)
        member1 = Wallet.create()
        member2 = Wallet.create()

        # Configure alice as a 2-of-2 multi-signature account.
        await sign_and_reliable_submission_async(
            SignerListSet(
                account=alice.address,
                signer_quorum=2,
                signer_entries=[
                    SignerEntry(account=member1.address, signer_weight=1),
                    SignerEntry(account=member2.address, signer_weight=1),
                ],
            ),
            alice,
            client,
        )

        batch = Batch(
            account=WALLET.address,
            flags=BatchFlag.TF_ALL_OR_NOTHING,
            raw_transactions=[
                Payment(
                    account=WALLET.address,
                    amount="1",
                    destination=alice.address,
                ),
                Payment(
                    account=alice.address,
                    amount="1",
                    destination=WALLET.address,
                ),
            ],
        )
        autofilled = await autofill(batch, client, 2)
        frag1 = sign_multiaccount_batch(
            member1, autofilled, multisign=True, batch_account=alice.address
        )
        frag2 = sign_multiaccount_batch(
            member2, autofilled, multisign=True, batch_account=alice.address
        )
        combined = Batch.from_blob(combine_batch_signers([frag1, frag2]))

        # Both members' signatures survive the combine.
        self.assertIsNotNone(combined.batch_signers)
        self.assertEqual(len(combined.batch_signers), 1)
        self.assertEqual(combined.batch_signers[0].account, alice.address)
        self.assertEqual(len(combined.batch_signers[0].signers), 2)

        response = await sign_and_reliable_submission_async(combined, WALLET, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

    # ── Sponsorship inside a Batch (XLS-68 §13) ────────────────────────────
    #
    # An inner transaction's SponsorSignature must stay an empty placeholder;
    # the sponsor's authorization comes from the outer BatchSigners instead.
    # rippled therefore counts the sponsor as a required Batch signer whenever
    # `Sponsor` and `SponsorSignature` are both present on an inner transaction,
    # and rejects the Batch with temBAD_SIGNER unless BatchSigners matches its
    # required set exactly.

    @test_async_and_sync(globals(), ["xrpl.transaction.autofill"])
    async def test_batch_with_reserve_sponsored_inner(self, client):
        """The sponsor of an inner transaction signs via BatchSigners."""
        sponsee = Wallet.create()
        sponsor = Wallet.create()
        await fund_wallet_async(sponsee)
        await fund_wallet_async(sponsor)

        # Inner 0: the sponsee creates a Check whose reserve the sponsor covers.
        # Inner 1: the outer account moves a drop, so the Batch has two inners.
        batch = Batch(
            account=WALLET.address,
            flags=BatchFlag.TF_ALL_OR_NOTHING,
            raw_transactions=[
                CheckCreate(
                    account=sponsee.address,
                    destination=DESTINATION.address,
                    send_max="1000000",
                    sponsor=sponsor.address,
                    sponsor_flags=2,  # spfSponsorReserve
                    sponsor_signature=SponsorSignature(),  # empty placeholder
                ),
                Payment(
                    account=WALLET.address,
                    amount="1",
                    destination=DESTINATION.address,
                ),
            ],
        )
        autofilled = await autofill(batch, client, 2)

        # Required signers: the sponsee (inner-0 authorizer) and the sponsor.
        # The outer account signs the Batch itself and must not be a BatchSigner.
        combined = Batch.from_blob(
            combine_batch_signers(
                [
                    sign_multiaccount_batch(sponsee, autofilled),
                    sign_multiaccount_batch(sponsor, autofilled),
                ]
            )
        )
        signers = [signer.account for signer in combined.batch_signers]
        self.assertEqual(set(signers), {sponsee.address, sponsor.address})
        self.assertNotIn(WALLET.address, signers)

        response = await sign_and_reliable_submission_async(combined, WALLET, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # The Check exists and records the sponsor that covers its reserve.
        objects = await client.request(
            AccountObjects(account=sponsee.address, type=AccountObjectType.CHECK)
        )
        checks = objects.result["account_objects"]
        self.assertEqual(len(checks), 1)
        self.assertEqual(checks[0].get("Sponsor"), sponsor.address)

    @test_async_and_sync(globals(), ["xrpl.transaction.autofill"])
    async def test_outer_batch_fee_sponsored(self, client):
        """The outer Batch may be fee-sponsored; the sponsor co-signs it."""
        sponsor = Wallet.create()
        await fund_wallet_async(sponsor)

        batch = Batch(
            account=WALLET.address,
            flags=BatchFlag.TF_ALL_OR_NOTHING,
            raw_transactions=[
                Payment(
                    account=WALLET.address,
                    amount="1",
                    destination=DESTINATION.address,
                ),
                Payment(
                    account=WALLET.address,
                    amount="1",
                    destination=DESTINATION.address,
                ),
            ],
            sponsor=sponsor.address,
            sponsor_flags=1,  # spfSponsorFee
        )
        autofilled = await autofill(batch, client)
        # The outer account's SigningPubKey must be settled before the sponsor
        # signs, because it is a signing field (XLS-68 §3.2 step 1).
        prepared = Batch.from_dict(
            {**autofilled.to_dict(), "signing_pub_key": WALLET.public_key}
        )
        sponsor_signed = sign_as_sponsor(sponsor, prepared).tx
        self.assertIsNotNone(sponsor_signed.sponsor_signature)

        response = await sign_and_reliable_submission_async(
            sponsor_signed, WALLET, client
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")
