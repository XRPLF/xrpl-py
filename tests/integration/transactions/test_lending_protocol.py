import datetime

from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    fund_wallet_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from xrpl.asyncio.transaction import autofill_and_sign, submit
from xrpl.core.binarycodec import encode_for_signing
from xrpl.core.keypairs.main import sign
from xrpl.models import (
    AccountObjects,
    AccountSet,
    AccountSetAsfFlag,
    LoanBrokerSet,
    LoanDelete,
    LoanManage,
    LoanPay,
    LoanSet,
    Transaction,
    VaultCreate,
    VaultDeposit,
)
from xrpl.models.currencies.xrp import XRP
from xrpl.models.requests.account_objects import AccountObjectType
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions.loan_manage import LoanManageFlag
from xrpl.models.transactions.loan_set import CounterpartySignature
from xrpl.models.transactions.vault_create import WithdrawalPolicy
from xrpl.wallet import Wallet


class TestLendingProtocolLifecycle(IntegrationTestCase):
    @test_async_and_sync(
        globals(), ["xrpl.transaction.autofill_and_sign", "xrpl.transaction.submit"]
    )
    async def test_lending_protocol_lifecycle(self, client):

        loan_issuer = Wallet.create()
        await fund_wallet_async(loan_issuer)

        depositor_wallet = Wallet.create()
        await fund_wallet_async(depositor_wallet)
        borrower_wallet = Wallet.create()
        await fund_wallet_async(borrower_wallet)

        # Step-0: Set up the relevant flags on the loan_issuer account -- This is
        # a pre-requisite for a Vault to hold the Issued Currency Asset
        response = await sign_and_reliable_submission_async(
            AccountSet(
                account=loan_issuer.classic_address,
                set_flag=AccountSetAsfFlag.ASF_DEFAULT_RIPPLE,
            ),
            loan_issuer,
        )
        self.assertTrue(response.is_successful())
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # Step-1: Create a vault
        tx = VaultCreate(
            account=loan_issuer.address,
            asset=XRP(),
            assets_maximum="1000",
            withdrawal_policy=WithdrawalPolicy.VAULT_STRATEGY_FIRST_COME_FIRST_SERVE,
        )
        response = await sign_and_reliable_submission_async(tx, loan_issuer, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        account_objects_response = await client.request(
            AccountObjects(account=loan_issuer.address, type=AccountObjectType.VAULT)
        )
        self.assertEqual(len(account_objects_response.result["account_objects"]), 1)
        VAULT_ID = account_objects_response.result["account_objects"][0]["index"]

        # Step-2: Create a loan broker
        tx = LoanBrokerSet(
            account=loan_issuer.address,
            vault_id=VAULT_ID,
        )
        response = await sign_and_reliable_submission_async(tx, loan_issuer, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # Step-2.1: Verify that the LoanBroker was successfully created
        response = await client.request(
            AccountObjects(
                account=loan_issuer.address, type=AccountObjectType.LOAN_BROKER
            )
        )
        self.assertEqual(len(response.result["account_objects"]), 1)
        LOAN_BROKER_ID = response.result["account_objects"][0]["index"]

        # Step-3: Deposit funds into the vault
        tx = VaultDeposit(
            account=depositor_wallet.address,
            vault_id=VAULT_ID,
            amount="100",
        )
        response = await sign_and_reliable_submission_async(
            tx, depositor_wallet, client
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # Step-5: The Loan Broker and Borrower create a Loan object with a LoanSet
        # transaction and the requested principal (excluding fees) is transered to
        # the Borrower.

        loan_issuer_signed_txn = await autofill_and_sign(
            LoanSet(
                account=loan_issuer.address,
                loan_broker_id=LOAN_BROKER_ID,
                principal_requested="100",
                start_date=int(datetime.datetime.now().timestamp()),
                counterparty=borrower_wallet.address,
            ),
            client,
            loan_issuer,
        )

        # borrower agrees to the terms of the loan
        borrower_txn_signature = sign(
            encode_for_signing(loan_issuer_signed_txn.to_xrpl()),
            borrower_wallet.private_key,
        )

        loan_issuer_and_borrower_signature = loan_issuer_signed_txn.to_dict()
        loan_issuer_and_borrower_signature["counterparty_signature"] = (
            CounterpartySignature(
                signing_pub_key=borrower_wallet.public_key,
                txn_signature=borrower_txn_signature,
            )
        )

        response = await submit(
            Transaction.from_dict(loan_issuer_and_borrower_signature),
            client,
            fail_hard=True,
        )

        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # fetch the Loan object
        response = await client.request(
            AccountObjects(account=borrower_wallet.address, type=AccountObjectType.LOAN)
        )
        self.assertEqual(len(response.result["account_objects"]), 1)
        LOAN_ID = response.result["account_objects"][0]["index"]

        # Delete the Loan object
        tx = LoanDelete(
            account=loan_issuer.address,
            loan_id=LOAN_ID,
        )
        response = await sign_and_reliable_submission_async(tx, loan_issuer, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        # Loan cannot be deleted until all the remaining payments are completed
        self.assertEqual(response.result["engine_result"], "tecHAS_OBLIGATIONS")

        # Test the LoanManage transaction
        tx = LoanManage(
            account=loan_issuer.address,
            loan_id=LOAN_ID,
            flags=LoanManageFlag.TF_LOAN_IMPAIR,
        )
        response = await sign_and_reliable_submission_async(tx, loan_issuer, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # Test the LoanPay transaction
        tx = LoanPay(
            account=borrower_wallet.address,
            loan_id=LOAN_ID,
            amount="100",
        )
        response = await sign_and_reliable_submission_async(tx, borrower_wallet, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        # The borrower cannot pay the loan before the start date
        self.assertEqual(response.result["engine_result"], "tecTOO_SOON")
