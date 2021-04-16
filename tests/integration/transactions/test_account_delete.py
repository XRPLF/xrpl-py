from unittest import TestCase

from tests.integration.it_utils import JSON_RPC_CLIENT, submit_transaction
from tests.integration.reusable_values import DESTINATION, WALLET
from xrpl.models.exceptions import XRPLException
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import AccountDelete

# We can re-use the shared wallet bc this test should fail to actually delete
# the associated account.
ACCOUNT = WALLET.classic_address

# AccountDelete transactions have a special fee.
# See https://xrpl.org/accountdelete.html#special-transaction-cost.
FEE = "5000000"

DESTINATION_TAG = 3


class TestAccountDelete(TestCase):
    def test_all_fields(self):
        account_delete = AccountDelete(
            account=ACCOUNT,
            fee=FEE,
            sequence=WALLET.sequence,
            destination=DESTINATION.classic_address,
            destination_tag=DESTINATION_TAG,
        )
        response = submit_transaction(account_delete, WALLET, JSON_RPC_CLIENT, False)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        WALLET.sequence += 1

        # Note, we can't test the `engine_result` without waiting a significant
        # amount of time because accounts can't be deleted until some number of
        # ledgers have closed since its creation.
        #
        # The documentation for `tecTOO_SOON` reads:
        # "The AccountDelete transaction failed because the account to be deleted had a
        # Sequence number that is too high. The current ledger index must be at least
        # 256 higher than the account's sequence number."
        # self.assertEqual(response.result['engine_result'], 'tesSUCCESS')

    def test_high_fee_unauthorized(self):
        # We expect an XRPLException to be raised
        with self.assertRaises(XRPLException):
            # GIVEN a new AccountDelete transaction
            account_delete = AccountDelete(
                account=ACCOUNT,
                # WITH fee higher than 2 XRP
                fee=FEE,
                sequence=WALLET.sequence,
                destination=DESTINATION.classic_address,
                destination_tag=DESTINATION_TAG,
            )
            submit_transaction(account_delete, WALLET)
