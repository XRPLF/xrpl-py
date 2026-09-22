"""Fee calculation for sponsored transactions.

Fee *arithmetic* lives here. The submission entry points threading the signer
counts into that arithmetic are covered in ``test_main.py`` (`sign_and_submit`,
`autofill_and_sign`) and ``test_reliable_submission.py` (`submit_and_wait`).
"""

from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, patch

from xrpl.asyncio.transaction.main import _calculate_fee_per_transaction_type, autofill
from xrpl.models.transactions import Batch, Payment, SponsorSignature
from xrpl.models.transactions.batch import BatchFlag
from xrpl.models.transactions.transaction import TransactionFlag

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_DESTINATION = "ra5nK24KXen9AHvsdFTKHSANinZseWnPcX"
_SPONSOR = "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn"
_BASE_FEE = "10"
_PUB_KEY = "ED" + "00" * 32
_SIG = "AB" * 32


class TestSponsorFeeCalculation(IsolatedAsyncioTestCase):
    """Fee autofill for sponsored transactions.

    rippled requires ``base * (1 + |tx.Signers| + |tx.SponsorSignature.Signers|)``
    (``Transactor::calculateBaseFee``), so only a *multi-signed* sponsor adds
    anything -- a lone sponsor signature and a pre-funded sponsorship are both
    billed as zero.

    ``SponsorSignature`` is always absent when the fee is computed, because
    ``Fee`` is a signing field and must be final before the sponsor signs. The
    sponsor's count is therefore declared via ``sponsor_signers_count`` rather
    than read from the transaction, and neither the sponsor's SignerList nor the
    existence of a ``Sponsorship`` object may influence it.
    """

    @staticmethod
    def _payment(**kwargs) -> Payment:
        return Payment(
            account=_ACCOUNT,
            destination=_DESTINATION,
            amount="1000",
            sequence=1,
            **kwargs,
        )

    async def _fee(self, transaction: Payment, **kwargs) -> str:
        with patch(
            "xrpl.asyncio.transaction.main.get_fee",
            new=AsyncMock(return_value=_BASE_FEE),
        ):
            return await _calculate_fee_per_transaction_type(
                transaction, client=None, **kwargs
            )

    async def test_unsponsored(self):
        """Baseline: an ordinary transaction pays one base fee."""
        self.assertEqual(await self._fee(self._payment()), "10")

    async def test_pre_funded_adds_nothing(self):
        """No SponsorSignature -> no sponsor signers -> no extra fee.

        The pre-funded flow draws the fee from Sponsorship.FeeAmount, capped by
        Sponsorship.MaxFee, so an over-estimate here would be rejected outright
        with terINSUF_FEE_B rather than merely overpaying.
        """
        tx = self._payment(sponsor=_SPONSOR, sponsor_flags=1)
        self.assertEqual(await self._fee(tx), "10")

    async def test_single_sig_sponsor_adds_nothing(self):
        """A lone sponsor signature is not billed.

        Transactor::calculateBaseFee counts only SponsorSignature.Signers. This
        differs from LoanSet::calculateBaseFee, which does bill a lone
        CounterpartySignature -- the two must not be conflated.
        """
        tx = self._payment(
            sponsor=_SPONSOR,
            sponsor_flags=1,
            sponsor_signature=SponsorSignature(
                signing_pub_key=_PUB_KEY, txn_signature=_SIG
            ),
        )
        self.assertEqual(await self._fee(tx), "10")

    async def test_empty_batch_inner_placeholder_adds_nothing(self):
        """An empty SponsorSignature placeholder is not billed.

        A Batch inner transaction naming a sponsor carries an empty
        placeholder; it has no Signers, so it contributes nothing.
        """
        tx = self._payment(
            sponsor=_SPONSOR,
            sponsor_flags=2,
            sponsor_signature=SponsorSignature(),
        )
        self.assertEqual(await self._fee(tx), "10")

    async def test_sponsor_signer_list_is_not_consulted(self):
        """The sponsor's account is never queried for the fee calculation.

        A SignerList is a capability, not a commitment, so a lookup would both
        cost a round trip and over-charge every sponsor that has one and
        single-signs.
        """
        tx = self._payment(sponsor=_SPONSOR, sponsor_flags=1)
        with patch(
            "xrpl.asyncio.transaction.main._fetch_counterparty_signers_count",
            new=AsyncMock(return_value=99),
        ) as mocked_lookup:
            fee = await self._fee(tx, sponsor_signers_count=1)

        mocked_lookup.assert_not_called()
        self.assertEqual(fee, "20")

    async def test_explicit_sponsor_signers_count(self):
        """`sponsor_signers_count` covers the autofill case.

        This is the only way to get a correct fee for a multi-signing sponsor:
        `Fee` is a signing field, so it is final before the sponsor signs, which
        means SponsorSignature is necessarily absent at autofill time. Mirrors
        `signers_count` for an ordinary multisigned transaction.
        """
        tx = self._payment(sponsor=_SPONSOR, sponsor_flags=1)
        self.assertEqual(await self._fee(tx, sponsor_signers_count=3), "40")

    async def test_explicit_count_combines_with_sponsee_signers(self):
        """Both declared counts are billed -> base * (1 + 2 + 3)."""
        tx = self._payment(sponsor=_SPONSOR, sponsor_flags=1)
        self.assertEqual(
            await self._fee(tx, signers_count=2, sponsor_signers_count=3), "60"
        )

    async def test_explicit_count_of_zero_adds_nothing(self):
        """Zero is the pre-funded/single-sign case and must not be billed."""
        tx = self._payment(sponsor=_SPONSOR, sponsor_flags=1)
        self.assertEqual(await self._fee(tx, sponsor_signers_count=0), "10")

    async def test_explicit_count_applies_alongside_empty_placeholder(self):
        """A present-but-empty SponsorSignature must not suppress the count.

        `simulate` and Batch inner transactions both carry an empty
        SponsorSignature.
        """
        tx = self._payment(
            sponsor=_SPONSOR,
            sponsor_flags=1,
            sponsor_signature=SponsorSignature(),
        )
        self.assertEqual(await self._fee(tx, sponsor_signers_count=3), "40")

    async def test_unsponsored_ignores_explicit_count(self):
        """No `sponsor` field means nothing to bill.

        rippled rejects a SponsorSignature with no accompanying Sponsor, so a
        count supplied without one can only over-estimate.
        """
        tx = self._payment()
        self.assertEqual(await self._fee(tx, sponsor_signers_count=3), "10")

    async def test_batch_with_reserve_sponsored_inner(self):
        """A reserve-sponsored inner transaction adds nothing to the Batch fee.

        Batch is `base * 2 + sum(inner fees)`. No sponsor count is threaded into
        the inner recursion, and none is needed: rippled rejects `Sponsor` plus
        fee sponsorship on an inner transaction (Batch.cpp, temINVALID_FLAG), and
        reserve sponsorship does not affect the fee.
        """
        inner = self._payment(
            sponsor=_SPONSOR,
            sponsor_flags=2,
            sponsor_signature=SponsorSignature(),
            flags=TransactionFlag.TF_INNER_BATCH_TXN.value,
        )
        batch = Batch(
            account=_ACCOUNT,
            raw_transactions=[inner, inner],
            flags=BatchFlag.TF_ALL_OR_NOTHING.value,
            sequence=1,
        )
        # base * 2 + (10 + 10)
        self.assertEqual(await self._fee(batch), "40")


class TestSponsorFeeAutofill(IsolatedAsyncioTestCase):
    """`sponsor_signers_count` reaching the fee through the public `autofill`.

    The tests above call ``_calculate_fee_per_transaction_type`` directly. These
    cover the threading in between, which is what callers actually use.
    """

    @staticmethod
    def _payment(**kwargs) -> Payment:
        return Payment(
            account=_ACCOUNT,
            destination=_DESTINATION,
            amount="1000",
            sequence=1,
            last_ledger_sequence=100,
            sponsor=_SPONSOR,
            sponsor_flags=1,
            **kwargs,
        )

    async def test_autofill_applies_sponsor_signers_count(self):
        """base * (1 + 3) must reach `transaction.fee`."""
        with (
            patch(
                "xrpl.asyncio.transaction.main.get_fee",
                new=AsyncMock(return_value=_BASE_FEE),
            ),
            patch(
                "xrpl.asyncio.transaction.main.get_network_id_and_build_version",
                new=AsyncMock(),
            ),
            patch(
                "xrpl.asyncio.transaction.main._tx_needs_networkID",
                return_value=False,
            ),
        ):
            filled = await autofill(self._payment(), None, sponsor_signers_count=3)

        self.assertEqual(filled.fee, "40")
