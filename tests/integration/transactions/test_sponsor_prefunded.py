"""Integration tests for pre-funded sponsorship (XLS-0068 §3.3).

The pre-funded flow is the headline convenience of the amendment: the sponsor
creates a ``Sponsorship`` object once, and thereafter the sponsee submits
sponsored transactions **alone**. No ``SponsorSignature`` is present and the
sponsor takes no part in signing or submission.

Fees are drawn from ``Sponsorship.FeeAmount`` (capped by ``MaxFee``) and
sponsored object reserves are drawn from ``Sponsorship.RemainingOwnerCount``.

NOTE: These tests assume the *featureSponsor* amendment is enabled on the
rippled server being tested against.

NOTE: Everything is inlined rather than factored into helpers on purpose --
``test_async_and_sync`` builds the sync variant by stripping ``await`` from the
method source, so an ``async def`` helper would return an un-awaited coroutine.
"""

from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    LEDGER_ACCEPT_REQUEST,
    fund_wallet_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from xrpl.asyncio.transaction import autofill, submit
from xrpl.asyncio.transaction.main import sign
from xrpl.models import CheckCreate, Payment, SponsorshipSet
from xrpl.models.requests.ledger_entry import LedgerEntry, Sponsorship
from xrpl.models.response import ResponseStatus
from xrpl.wallet import Wallet

# Sponsor-type flags (XLS-0068).
_TF_SPONSOR_FEE = 0x00000001
_TF_SPONSOR_RESERVE = 0x00000002

_FEE_BUDGET = "2000000"
_OWNER_COUNT_BUDGET = 5


class TestPreFundedSponsorship(IntegrationTestCase):
    @test_async_and_sync(
        globals(), ["xrpl.transaction.autofill", "xrpl.transaction.submit"]
    )
    async def test_prefunded_fee_no_sponsor_signature(self, client):
        """Sponsee submits alone; the fee comes out of Sponsorship.FeeAmount."""
        sponsor_wallet = Wallet.create()
        sponsee_wallet = Wallet.create()
        destination_wallet = Wallet.create()
        await fund_wallet_async(sponsor_wallet)
        await fund_wallet_async(sponsee_wallet)
        await fund_wallet_async(destination_wallet)

        # Sponsor pre-funds the relationship. The sponsee does nothing to accept.
        create_resp = await sign_and_reliable_submission_async(
            SponsorshipSet(
                account=sponsor_wallet.address,
                sponsee=sponsee_wallet.address,
                fee_amount_delta=_FEE_BUDGET,
            ),
            sponsor_wallet,
            client,
        )
        self.assertEqual(create_resp.result["engine_result"], "tesSUCCESS")

        before_resp = await client.request(
            LedgerEntry(
                sponsorship=Sponsorship(
                    sponsor=sponsor_wallet.address, sponsee=sponsee_wallet.address
                )
            )
        )
        self.assertEqual(before_resp.result["node"]["FeeAmount"], _FEE_BUDGET)

        sponsee_before = await client.request(
            LedgerEntry(account_root=sponsee_wallet.address)
        )
        balance_before = int(sponsee_before.result["node"]["Balance"])

        payment = Payment(
            account=sponsee_wallet.address,
            destination=destination_wallet.address,
            amount="1000000",
            sponsor=sponsor_wallet.address,
            sponsor_flags=_TF_SPONSOR_FEE,
        )
        autofilled = await autofill(payment, client)
        # Pre-funded: no co-signature exists, and none is billed for.
        self.assertIsNone(autofilled.sponsor_signature)

        signed = sign(autofilled, sponsee_wallet)
        self.assertIsNone(signed.sponsor_signature)

        response = await submit(signed, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")
        await client.request(LEDGER_ACCEPT_REQUEST)

        # The budget paid the fee.
        after_resp = await client.request(
            LedgerEntry(
                sponsorship=Sponsorship(
                    sponsor=sponsor_wallet.address, sponsee=sponsee_wallet.address
                )
            )
        )
        remaining = int(after_resp.result["node"].get("FeeAmount", "0"))
        self.assertEqual(int(_FEE_BUDGET) - remaining, int(autofilled.fee))

        # The sponsee paid only the Payment amount, never the fee.
        sponsee_after = await client.request(
            LedgerEntry(account_root=sponsee_wallet.address)
        )
        balance_after = int(sponsee_after.result["node"]["Balance"])
        self.assertEqual(balance_before - balance_after, int(payment.amount))

    @test_async_and_sync(
        globals(), ["xrpl.transaction.autofill", "xrpl.transaction.submit"]
    )
    async def test_prefunded_reserve_no_sponsor_signature(self, client):
        """A sponsored object reserve is drawn from RemainingOwnerCount."""
        sponsor_wallet = Wallet.create()
        sponsee_wallet = Wallet.create()
        destination_wallet = Wallet.create()
        await fund_wallet_async(sponsor_wallet)
        await fund_wallet_async(sponsee_wallet)
        await fund_wallet_async(destination_wallet)

        create_resp = await sign_and_reliable_submission_async(
            SponsorshipSet(
                account=sponsor_wallet.address,
                sponsee=sponsee_wallet.address,
                fee_amount_delta=_FEE_BUDGET,
                remaining_owner_count_delta=_OWNER_COUNT_BUDGET,
            ),
            sponsor_wallet,
            client,
        )
        self.assertEqual(create_resp.result["engine_result"], "tesSUCCESS")

        before_resp = await client.request(
            LedgerEntry(
                sponsorship=Sponsorship(
                    sponsor=sponsor_wallet.address, sponsee=sponsee_wallet.address
                )
            )
        )
        self.assertEqual(
            before_resp.result["node"]["RemainingOwnerCount"], _OWNER_COUNT_BUDGET
        )

        check = CheckCreate(
            account=sponsee_wallet.address,
            destination=destination_wallet.address,
            send_max="1000000",
            sponsor=sponsor_wallet.address,
            sponsor_flags=_TF_SPONSOR_RESERVE,
        )
        autofilled = await autofill(check, client)
        self.assertIsNone(autofilled.sponsor_signature)

        response = await submit(sign(autofilled, sponsee_wallet), client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")
        await client.request(LEDGER_ACCEPT_REQUEST)

        # One sponsored object created -> one count consumed.
        after_resp = await client.request(
            LedgerEntry(
                sponsorship=Sponsorship(
                    sponsor=sponsor_wallet.address, sponsee=sponsee_wallet.address
                )
            )
        )
        self.assertEqual(
            after_resp.result["node"]["RemainingOwnerCount"],
            _OWNER_COUNT_BUDGET - 1,
        )

    @test_async_and_sync(
        globals(), ["xrpl.transaction.autofill", "xrpl.transaction.submit"]
    )
    async def test_prefunded_fee_over_max_fee_rejected(self, client):
        """MaxFee caps the spendable fee even when FeeAmount is larger.

        rippled computes spendable = min(FeeAmount, MaxFee) and refuses a Fee
        above it rather than spending part of it. This is why the fee autofill
        must not over-estimate for a pre-funded sponsorship.
        """
        sponsor_wallet = Wallet.create()
        sponsee_wallet = Wallet.create()
        destination_wallet = Wallet.create()
        await fund_wallet_async(sponsor_wallet)
        await fund_wallet_async(sponsee_wallet)
        await fund_wallet_async(destination_wallet)

        create_resp = await sign_and_reliable_submission_async(
            SponsorshipSet(
                account=sponsor_wallet.address,
                sponsee=sponsee_wallet.address,
                fee_amount_delta=_FEE_BUDGET,
                max_fee="1",  # 1 drop: below any real transaction fee
            ),
            sponsor_wallet,
            client,
        )
        self.assertEqual(create_resp.result["engine_result"], "tesSUCCESS")

        payment = Payment(
            account=sponsee_wallet.address,
            destination=destination_wallet.address,
            amount="1000000",
            sponsor=sponsor_wallet.address,
            sponsor_flags=_TF_SPONSOR_FEE,
        )
        autofilled = await autofill(payment, client)
        self.assertGreater(int(autofilled.fee), 1)

        response = await submit(sign(autofilled, sponsee_wallet), client)
        self.assertIn(
            response.result["engine_result"],
            ("terINSUF_FEE_B", "tecINSUFF_FEE"),
        )
        # tecINSUFF_FEE is applied and included in a ledger, unlike the purely
        # local terINSUF_FEE_B, so close the ledger before reading state.
        await client.request(LEDGER_ACCEPT_REQUEST)

        # Nothing was spent from the budget.
        after_resp = await client.request(
            LedgerEntry(
                sponsorship=Sponsorship(
                    sponsor=sponsor_wallet.address, sponsee=sponsee_wallet.address
                )
            )
        )
        self.assertEqual(after_resp.result["node"]["FeeAmount"], _FEE_BUDGET)

    # -----------------------------------------------------------------------
    # Delta arithmetic on the Sponsorship object (XLS-68 §9.6)
    #
    # `FeeAmountDelta` and `RemainingOwnerCountDelta` are *changes*, not
    # replacements. A negative delta refunds/reduces, clamped so the result never
    # goes below zero, and a result of zero removes the field entirely.
    # -----------------------------------------------------------------------

    @test_async_and_sync(
        globals(), ["xrpl.transaction.autofill", "xrpl.transaction.submit"]
    )
    async def test_positive_then_negative_fee_delta(self, client):
        """A negative delta refunds XRP to the sponsor and lowers FeeAmount."""
        sponsor_wallet = Wallet.create()
        sponsee_wallet = Wallet.create()
        await fund_wallet_async(sponsor_wallet)
        await fund_wallet_async(sponsee_wallet)

        create_resp = await sign_and_reliable_submission_async(
            SponsorshipSet(
                account=sponsor_wallet.address,
                sponsee=sponsee_wallet.address,
                fee_amount_delta="3000000",
            ),
            sponsor_wallet,
            client,
        )
        self.assertEqual(create_resp.result["engine_result"], "tesSUCCESS")

        node = await client.request(
            LedgerEntry(
                sponsorship=Sponsorship(
                    sponsor=sponsor_wallet.address, sponsee=sponsee_wallet.address
                )
            )
        )
        self.assertEqual(node.result["node"]["FeeAmount"], "3000000")

        sponsor_before = await client.request(
            LedgerEntry(account_root=sponsor_wallet.address)
        )
        balance_before = int(sponsor_before.result["node"]["Balance"])

        # Refund 1 XRP of the budget back to the sponsor.
        reduce_resp = await sign_and_reliable_submission_async(
            SponsorshipSet(
                account=sponsor_wallet.address,
                sponsee=sponsee_wallet.address,
                fee_amount_delta="-1000000",
            ),
            sponsor_wallet,
            client,
        )
        self.assertEqual(reduce_resp.result["engine_result"], "tesSUCCESS")

        node = await client.request(
            LedgerEntry(
                sponsorship=Sponsorship(
                    sponsor=sponsor_wallet.address, sponsee=sponsee_wallet.address
                )
            )
        )
        self.assertEqual(node.result["node"]["FeeAmount"], "2000000")

        # The refund landed in the sponsor's balance, net of the transaction fee.
        sponsor_after = await client.request(
            LedgerEntry(account_root=sponsor_wallet.address)
        )
        balance_after = int(sponsor_after.result["node"]["Balance"])
        self.assertGreater(balance_after, balance_before)

    @test_async_and_sync(
        globals(), ["xrpl.transaction.autofill", "xrpl.transaction.submit"]
    )
    async def test_negative_fee_delta_clamps_and_clears_field(self, client):
        """An over-large negative delta clamps to zero and removes FeeAmount.

        The object survives because `RemainingOwnerCount` still provides a budget;
        without it the transaction would be rejected with tecNO_PERMISSION.
        """
        sponsor_wallet = Wallet.create()
        sponsee_wallet = Wallet.create()
        await fund_wallet_async(sponsor_wallet)
        await fund_wallet_async(sponsee_wallet)

        create_resp = await sign_and_reliable_submission_async(
            SponsorshipSet(
                account=sponsor_wallet.address,
                sponsee=sponsee_wallet.address,
                fee_amount_delta="1000000",
                remaining_owner_count_delta=4,
            ),
            sponsor_wallet,
            client,
        )
        self.assertEqual(create_resp.result["engine_result"], "tesSUCCESS")

        # Ask to remove far more than is held; rippled clamps to the balance.
        clamp_resp = await sign_and_reliable_submission_async(
            SponsorshipSet(
                account=sponsor_wallet.address,
                sponsee=sponsee_wallet.address,
                fee_amount_delta="-999000000",
            ),
            sponsor_wallet,
            client,
        )
        self.assertEqual(clamp_resp.result["engine_result"], "tesSUCCESS")

        node = await client.request(
            LedgerEntry(
                sponsorship=Sponsorship(
                    sponsor=sponsor_wallet.address, sponsee=sponsee_wallet.address
                )
            )
        )
        # Reaching zero clears the field rather than storing "0".
        self.assertNotIn("FeeAmount", node.result["node"])
        self.assertEqual(node.result["node"]["RemainingOwnerCount"], 4)

    @test_async_and_sync(
        globals(), ["xrpl.transaction.autofill", "xrpl.transaction.submit"]
    )
    async def test_negative_owner_count_delta_clamps_and_clears_field(self, client):
        """A negative count delta reduces the budget and clears it at zero."""
        sponsor_wallet = Wallet.create()
        sponsee_wallet = Wallet.create()
        await fund_wallet_async(sponsor_wallet)
        await fund_wallet_async(sponsee_wallet)

        create_resp = await sign_and_reliable_submission_async(
            SponsorshipSet(
                account=sponsor_wallet.address,
                sponsee=sponsee_wallet.address,
                fee_amount_delta="1000000",
                remaining_owner_count_delta=5,
            ),
            sponsor_wallet,
            client,
        )
        self.assertEqual(create_resp.result["engine_result"], "tesSUCCESS")

        reduce_resp = await sign_and_reliable_submission_async(
            SponsorshipSet(
                account=sponsor_wallet.address,
                sponsee=sponsee_wallet.address,
                remaining_owner_count_delta=-2,
            ),
            sponsor_wallet,
            client,
        )
        self.assertEqual(reduce_resp.result["engine_result"], "tesSUCCESS")

        node = await client.request(
            LedgerEntry(
                sponsorship=Sponsorship(
                    sponsor=sponsor_wallet.address, sponsee=sponsee_wallet.address
                )
            )
        )
        self.assertEqual(node.result["node"]["RemainingOwnerCount"], 3)

        # Overshoot: clamps to zero, and the field is removed. FeeAmount keeps
        # the object alive.
        clamp_resp = await sign_and_reliable_submission_async(
            SponsorshipSet(
                account=sponsor_wallet.address,
                sponsee=sponsee_wallet.address,
                remaining_owner_count_delta=-99,
            ),
            sponsor_wallet,
            client,
        )
        self.assertEqual(clamp_resp.result["engine_result"], "tesSUCCESS")

        node = await client.request(
            LedgerEntry(
                sponsorship=Sponsorship(
                    sponsor=sponsor_wallet.address, sponsee=sponsee_wallet.address
                )
            )
        )
        self.assertNotIn("RemainingOwnerCount", node.result["node"])
        self.assertEqual(node.result["node"]["FeeAmount"], "1000000")

    @test_async_and_sync(
        globals(), ["xrpl.transaction.autofill", "xrpl.transaction.submit"]
    )
    async def test_removing_all_budget_is_rejected(self, client):
        """Zeroing the only remaining budget leaves an unusable object.

        rippled returns tecNO_PERMISSION rather than keeping a Sponsorship that
        consumes the sponsor's reserve while providing nothing (XLS-68 §9.5).
        """
        sponsor_wallet = Wallet.create()
        sponsee_wallet = Wallet.create()
        await fund_wallet_async(sponsor_wallet)
        await fund_wallet_async(sponsee_wallet)

        create_resp = await sign_and_reliable_submission_async(
            SponsorshipSet(
                account=sponsor_wallet.address,
                sponsee=sponsee_wallet.address,
                fee_amount_delta="1000000",
            ),
            sponsor_wallet,
            client,
        )
        self.assertEqual(create_resp.result["engine_result"], "tesSUCCESS")

        remove_resp = await sign_and_reliable_submission_async(
            SponsorshipSet(
                account=sponsor_wallet.address,
                sponsee=sponsee_wallet.address,
                fee_amount_delta="-1000000",
            ),
            sponsor_wallet,
            client,
        )
        self.assertEqual(remove_resp.result["engine_result"], "tecNO_PERMISSION")

        # The object is untouched.
        node = await client.request(
            LedgerEntry(
                sponsorship=Sponsorship(
                    sponsor=sponsor_wallet.address, sponsee=sponsee_wallet.address
                )
            )
        )
        self.assertEqual(node.result["node"]["FeeAmount"], "1000000")
