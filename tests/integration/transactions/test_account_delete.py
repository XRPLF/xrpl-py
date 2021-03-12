from unittest import TestCase

from tests.integration.it_utils import JSON_RPC_CLIENT, submit_transaction
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import AccountDelete
from xrpl.wallet import generate_faucet_wallet

WALLET = generate_faucet_wallet(JSON_RPC_CLIENT)
DESTINATION_WALLET = generate_faucet_wallet(JSON_RPC_CLIENT)

ACCOUNT = WALLET.classic_address

# AccountDelete transactions have a special fee.
# See https://xrpl.org/accountdelete.html#special-transaction-cost.
FEE = "5000000"

DESTINATION_TAG = 3

# TODO: Figure out how to handle the `tecTOO_SOON` error code... Sleep??  It'd be long.
# See https://xrpl.org/accountdelete.html#error-cases


class TestAccountDelete(TestCase):
    def test_all_fields(self):
        account_delete = AccountDelete(
            account=ACCOUNT,
            fee=FEE,
            sequence=WALLET.next_sequence_num,
            destination=DESTINATION_WALLET.classic_address,
            destination_tag=DESTINATION_TAG,
        )
        response = submit_transaction(account_delete, WALLET)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)

        # Note, we can't test the `engine_result` without waiting a significant
        # amount of time because accounts can't be deleted until some number of
        # ledgers have closed since its creation.
        #
        # The documentation for `tecTOO_SOON` reads:
        # "The AccountDelete transaction failed because the account to be deleted had a
        # Sequence number that is too high. The current ledger index must be at least
        # 256 higher than the account's sequence number."
        # self.assertEqual(response.result['engine_result'], 'tesSUCCESS')
