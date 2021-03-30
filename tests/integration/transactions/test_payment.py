from unittest import TestCase

from tests.integration.it_utils import submit_transaction
from tests.integration.reusable_values import DESTINATION, FEE, WALLET
from xrpl.models.transactions import Payment


class TestPayment(TestCase):
    def test_basic_functionality(self):
        response = submit_transaction(
            Payment(
                account=WALLET.classic_address,
                sequence=WALLET.next_sequence_num,
                fee=FEE,
                amount="10",
                destination=DESTINATION.classic_address,
            ),
            WALLET,
        )
        self.assertTrue(response.is_successful())

    # def test_partial_payment_causes_warning(self):
    #     # this test is super brittle! commenting it out for now
    #
    #     # setup trust line
    #     send_reliable_submission(
    #         TrustSet(
    #             account=DESTINATION.classic_address,
    #             sequence=DESTINATION.next_sequence_num,
    #             last_ledger_sequence=DESTINATION.next_sequence_num + 10,
    #             fee=FEE,
    #             flags=TrustSetFlag.TF_SET_NO_RIPPLE,
    #             limit_amount=IssuedCurrencyAmount(
    #                 issuer=WALLET.classic_address,
    #                 currency="USD",
    #                 value="100",
    #             ),
    #         ),
    #         DESTINATION,
    #         JSON_RPC_CLIENT,
    #     )
    #
    #     # ensure that creating a partial payment warns
    #     with self.assertWarns(Warning):
    #         r = send_reliable_submission(
    #             Payment(
    #                 account=WALLET.classic_address,
    #                 sequence=WALLET.next_sequence_num,
    #                 last_ledger_sequence=WALLET.next_sequence_num + 10,
    #                 fee=FEE,
    #                 flags=PaymentFlag.TF_PARTIAL_PAYMENT,
    #                 amount=IssuedCurrencyAmount(
    #                     issuer=WALLET.classic_address,
    #                     currency="USD",
    #                     value="1",
    #                 ),
    #                 send_max=IssuedCurrencyAmount(
    #                     issuer=WALLET.classic_address,
    #                     currency="USD",
    #                     value="10",
    #                 ),
    #                 destination=DESTINATION.classic_address,
    #             ),
    #             WALLET,
    #             JSON_RPC_CLIENT,
    #         )
    #
    #     # ensure that retrieving the sent partial payment warns too
    #     with self.assertWarns(Warning):
    #         get_transaction_from_hash(r.result["hash"], JSON_RPC_CLIENT)
