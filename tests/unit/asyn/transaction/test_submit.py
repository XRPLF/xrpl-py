"""Unit tests for ``submit``."""

from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, Mock

from xrpl.asyncio.transaction.main import sign, submit
from xrpl.constants import XRPLException
from xrpl.models.transactions import Batch, BatchFlag, LoanSet, Payment
from xrpl.transaction.counterparty_signer import sign_loan_set_by_counterparty
from xrpl.wallet import Wallet

_BROKER = Wallet.from_seed("sEdT2fq1MdpXJdosNRZ1tuHk4qU3V2m")
_BORROWER = Wallet.from_seed("sEd7FqVHfNZ2UdGAwjssxPev2ujwJoT")
_LOAN_SET = LoanSet(
    account=_BROKER.address,
    counterparty=_BORROWER.address,
    loan_broker_id="033D9B59DBDC4F48FB6708892E7DB0E8FBF9710C3A181B99D9FAF7B9C82EF077",
    principal_requested="5000000",
    sequence=1,
    fee="24",
    last_ledger_sequence=12312,
)


def _client() -> Mock:
    client = Mock()
    client._request_impl = AsyncMock(
        return_value=Mock(is_successful=Mock(return_value=True))
    )
    return client


class TestSubmit(IsolatedAsyncioTestCase):
    async def test_raises_for_loan_set_without_counterparty_signature(self):
        client = _client()

        with self.assertRaises(XRPLException) as context:
            await submit(sign(_LOAN_SET, _BROKER), client)

        self.assertEqual(
            str(context.exception),
            "LoanSet requires the counterparty's signature (CounterpartySignature). "
            "Use sign_loan_set_by_counterparty before submitting.",
        )
        client._request_impl.assert_not_awaited()

    async def test_submits_loan_set_signed_by_counterparty(self):
        client = _client()
        signed = sign_loan_set_by_counterparty(_BORROWER, sign(_LOAN_SET, _BROKER))

        await submit(signed.tx, client)

        client._request_impl.assert_awaited_once()

    async def test_submits_batch_whose_inner_loan_set_has_no_counterparty_signature(
        self,
    ):
        client = _client()
        inner_fields = {"fee": "0", "signing_pub_key": ""}
        batch = Batch(
            account=_BROKER.address,
            flags=BatchFlag.TF_ALL_OR_NOTHING,
            sequence=1,
            fee="40",
            last_ledger_sequence=12312,
            raw_transactions=[
                LoanSet.from_dict(
                    {**_LOAN_SET.to_dict(), **inner_fields, "sequence": 2}
                ),
                Payment(
                    account=_BROKER.address,
                    destination=_BORROWER.address,
                    amount="1000000",
                    sequence=3,
                    **inner_fields,
                ),
            ],
        )

        await submit(sign(batch, _BROKER), client)

        client._request_impl.assert_awaited_once()
