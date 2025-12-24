from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import fund_wallet_async, test_async_and_sync
from xrpl.asyncio.transaction import autofill_and_sign
from xrpl.models.requests import Sign
from xrpl.models.transactions import LoanSet
from xrpl.wallet import Wallet

_SECRET = "randomsecretkey"
_LOAN_BROKER_ID = "D1B9DFF432B4F56127BE947281A327B656F202FC1530DD6409D771F7C4CA4F4B"
_COUNTERPARTY_ADDRESS = "rnFRDVZUV9GmqoUJ65gkaQnMEiAnCdxb2m"


class TestSign(IntegrationTestCase):
    @test_async_and_sync(globals(), ["xrpl.transaction.autofill_and_sign"])
    async def test_basic_functionality(self, client):
        loan_issuer = Wallet.create()
        await fund_wallet_async(loan_issuer)

        loan_issuer_signed_txn = await autofill_and_sign(
            LoanSet(
                account=loan_issuer.address,
                loan_broker_id=_LOAN_BROKER_ID,
                principal_requested="100",
                counterparty=_COUNTERPARTY_ADDRESS,
            ),
            client,
            loan_issuer,
        )
        response = await client.request(
            Sign(
                transaction=loan_issuer_signed_txn,
                signature_target="CounterpartySignature",
                secret=_SECRET,
            )
        )
        self.assertTrue(response.is_successful())
        self.assertTrue(response.result["tx_json"]["CounterpartySignature"] is not None)
        self.assertTrue(
            response.result["tx_json"]["CounterpartySignature"]["SigningPubKey"]
            is not None
        )
        self.assertTrue(
            response.result["tx_json"]["CounterpartySignature"]["TxnSignature"]
            is not None
        )
