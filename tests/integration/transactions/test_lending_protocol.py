from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    LEDGER_ACCEPT_REQUEST,
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
    Payment,
    Transaction,
    TrustSet,
    VaultCreate,
    VaultDeposit,
)
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.amounts.mpt_amount import MPTAmount
from xrpl.models.currencies.issued_currency import IssuedCurrency
from xrpl.models.currencies.mpt_currency import MPTCurrency
from xrpl.models.currencies.xrp import XRP
from xrpl.models.requests.account_objects import AccountObjectType
from xrpl.models.requests.tx import Tx
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions.loan_manage import LoanManageFlag
from xrpl.models.transactions.loan_set import CounterpartySignature
from xrpl.models.transactions.mptoken_authorize import MPTokenAuthorize
from xrpl.models.transactions.mptoken_issuance_create import (
    MPTokenIssuanceCreate,
    MPTokenIssuanceCreateFlag,
)
from xrpl.models.transactions.signer_list_set import SignerEntry, SignerListSet
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
        # transaction and the requested principal (excluding fees) is transferred to
        # the Borrower.

        loan_issuer_signed_txn = await autofill_and_sign(
            LoanSet(
                account=loan_issuer.address,
                loan_broker_id=LOAN_BROKER_ID,
                principal_requested="100",
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

        # Wait for the validation of the latest ledger
        await client.request(LEDGER_ACCEPT_REQUEST)

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
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

    @test_async_and_sync(
        globals(), ["xrpl.transaction.autofill_and_sign", "xrpl.transaction.submit"]
    )
    async def test_autofill_loan_set_txn_multisigned(self, client):
        loan_issuer = Wallet.create()
        await fund_wallet_async(loan_issuer)

        depositor_wallet = Wallet.create()
        await fund_wallet_async(depositor_wallet)
        borrower_wallet = Wallet.create()
        await fund_wallet_async(borrower_wallet)

        borrower_signer1 = Wallet.create()
        await fund_wallet_async(borrower_signer1)
        borrower_signer2 = Wallet.create()
        await fund_wallet_async(borrower_signer2)

        # Setup borrower wallet with multiple signers to validate the correctness
        # of the fees-autofill logic.
        NUM_SIGNERS = 2
        tx = SignerListSet(
            account=borrower_wallet.address,
            signer_quorum=NUM_SIGNERS,
            signer_entries=[
                SignerEntry(account=borrower_signer1.address, signer_weight=1),
                SignerEntry(account=borrower_signer2.address, signer_weight=1),
            ],
        )
        response = await sign_and_reliable_submission_async(tx, borrower_wallet, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
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

        # Step-5.A: The Loan Broker and Borrower create a Loan object with a LoanSet
        # transaction and the requested principal (excluding fees) is transferred to
        # the Borrower.

        loan_issuer_signed_txn = await autofill_and_sign(
            LoanSet(
                account=loan_issuer.address,
                loan_broker_id=LOAN_BROKER_ID,
                principal_requested="100",
                counterparty=borrower_wallet.address,
            ),
            client,
            loan_issuer,
        )

        # Note: The transaction reference fee is specified in the rippled.cfg file for
        # integration tests.
        self.assertEqual(
            loan_issuer_signed_txn.fee,
            str(200 + NUM_SIGNERS * 200),
        )

        # Step-5.B: borrower agrees to the terms of the loan
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

        # Wait for the validation of the latest ledger
        await client.request(LEDGER_ACCEPT_REQUEST)

        # fetch the Loan object
        response = await client.request(
            AccountObjects(account=borrower_wallet.address, type=AccountObjectType.LOAN)
        )
        self.assertEqual(len(response.result["account_objects"]), 1)

    @test_async_and_sync(
        globals(), ["xrpl.transaction.autofill_and_sign", "xrpl.transaction.submit"]
    )
    async def test_loan_set_txn_counterparty_is_loan_broker_owner(self, client):
        loan_issuer = Wallet.create()
        await fund_wallet_async(loan_issuer)

        depositor_wallet = Wallet.create()
        await fund_wallet_async(depositor_wallet)

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

        # Step-5.A: The Loan Broker and Borrower (Borrower is the Owner of the
        # LoanBroker, i.e. loan_issuer account) create a Loan object with a LoanSet
        # transaction and the requested principal (excluding fees) is transferred to
        # the Borrower.
        borrower_wallet: Wallet = loan_issuer

        loan_issuer_signed_txn = await autofill_and_sign(
            LoanSet(
                account=loan_issuer.address,
                loan_broker_id=LOAN_BROKER_ID,
                principal_requested="100",
            ),
            client,
            loan_issuer,
        )

        # The loan_issuer is involved in both sides of this transaction.
        self.assertEqual(
            loan_issuer_signed_txn.fee,
            str(200 + 200),
            # Usual transaction reference fee and additional fee for the counterparty
            # signature. Note: Multi-signing is not enabled on the loan_issuer account.
        )

        # Step-5.B: borrower agrees to the terms of the loan
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

        # Wait for the validation of the latest ledger
        await client.request(LEDGER_ACCEPT_REQUEST)

        # fetch the Loan object
        response = await client.request(
            AccountObjects(account=borrower_wallet.address, type=AccountObjectType.LOAN)
        )
        self.assertEqual(len(response.result["account_objects"]), 1)

    @test_async_and_sync(
        globals(), ["xrpl.transaction.autofill_and_sign", "xrpl.transaction.submit"]
    )
    async def test_lending_protocol_lifecycle_with_iou_asset(self, client):
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

        # Step 0.1: Set up trustlines required for the transferring the IOU token
        tx = TrustSet(
            account=depositor_wallet.address,
            limit_amount=IssuedCurrencyAmount(
                currency="USD", issuer=loan_issuer.address, value="1000"
            ),
        )
        response = await sign_and_reliable_submission_async(
            tx, depositor_wallet, client
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        tx = TrustSet(
            account=borrower_wallet.address,
            limit_amount=IssuedCurrencyAmount(
                currency="USD", issuer=loan_issuer.address, value="1000"
            ),
        )
        response = await sign_and_reliable_submission_async(tx, borrower_wallet, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # Step 0.2: Transfer the `USD` IOU to depositor_wallet and borrower_wallet
        tx = Payment(
            account=loan_issuer.address,
            destination=depositor_wallet.address,
            amount=IssuedCurrencyAmount(
                currency="USD", issuer=loan_issuer.address, value="1000"
            ),
        )
        response = await sign_and_reliable_submission_async(tx, loan_issuer, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        tx = Payment(
            account=loan_issuer.address,
            destination=borrower_wallet.address,
            amount=IssuedCurrencyAmount(
                currency="USD", issuer=loan_issuer.address, value="1000"
            ),
        )
        response = await sign_and_reliable_submission_async(tx, loan_issuer, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # Step-1: Create a vault
        tx = VaultCreate(
            account=loan_issuer.address,
            asset=IssuedCurrency(currency="USD", issuer=loan_issuer.address),
            assets_maximum="10000",
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
            debt_maximum="10000",
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
            amount=IssuedCurrencyAmount(
                currency="USD", issuer=loan_issuer.address, value="1000"
            ),
        )
        response = await sign_and_reliable_submission_async(
            tx, depositor_wallet, client
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # Step-5: The Loan Broker and Borrower create a Loan object with a LoanSet
        # transaction and the requested principal (excluding fees) is transferred to
        # the Borrower.
        loan_issuer_signed_txn = await autofill_and_sign(
            LoanSet(
                account=loan_issuer.address,
                loan_broker_id=LOAN_BROKER_ID,
                principal_requested="100",
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

        # Wait for the validation of the latest ledger
        await client.request(LEDGER_ACCEPT_REQUEST)

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
            amount=IssuedCurrencyAmount(
                currency="USD", issuer=loan_issuer.address, value="100"
            ),
        )
        response = await sign_and_reliable_submission_async(tx, borrower_wallet, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

    @test_async_and_sync(globals(), async_only=True)
    async def test_lending_protocol_lifecycle_with_mpt_asset(self, client):
        loan_issuer = Wallet.create()
        await fund_wallet_async(loan_issuer)

        depositor_wallet = Wallet.create()
        await fund_wallet_async(depositor_wallet)
        borrower_wallet = Wallet.create()
        await fund_wallet_async(borrower_wallet)

        # Step-0: issue the MPT
        tx = MPTokenIssuanceCreate(
            account=loan_issuer.address,
            maximum_amount="5000",
            flags=MPTokenIssuanceCreateFlag.TF_MPT_CAN_TRANSFER,
        )
        response = await sign_and_reliable_submission_async(tx, loan_issuer, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        tx_hash = response.result["tx_json"]["hash"]
        tx_res = await client.request(Tx(transaction=tx_hash))
        MPT_ISSUANCE_ID = tx_res.result["meta"]["mpt_issuance_id"]

        # validate that the MPTIssuance was created
        account_objects_response = await client.request(
            AccountObjects(
                account=loan_issuer.address, type=AccountObjectType.MPT_ISSUANCE
            )
        )
        self.assertEqual(len(account_objects_response.result["account_objects"]), 1)
        self.assertEqual(
            account_objects_response.result["account_objects"][0]["mpt_issuance_id"],
            MPT_ISSUANCE_ID,
        )

        # Step 0.2: Authorize the destination wallets to hold the MPT
        response = await sign_and_reliable_submission_async(
            MPTokenAuthorize(
                account=depositor_wallet.classic_address,
                mptoken_issuance_id=MPT_ISSUANCE_ID,
            ),
            depositor_wallet,
            client,
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        response = await sign_and_reliable_submission_async(
            MPTokenAuthorize(
                account=borrower_wallet.classic_address,
                mptoken_issuance_id=MPT_ISSUANCE_ID,
            ),
            borrower_wallet,
            client,
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # Step 0.3: Send some MPT to the depositor_wallet and borrower_wallet
        tx = Payment(
            account=loan_issuer.address,
            destination=depositor_wallet.address,
            amount=MPTAmount(mpt_issuance_id=MPT_ISSUANCE_ID, value="1000"),
        )
        response = await sign_and_reliable_submission_async(tx, loan_issuer, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        tx = Payment(
            account=loan_issuer.address,
            destination=borrower_wallet.address,
            amount=MPTAmount(mpt_issuance_id=MPT_ISSUANCE_ID, value="1000"),
        )
        response = await sign_and_reliable_submission_async(tx, loan_issuer, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # Step-1: Create a vault
        tx = VaultCreate(
            account=loan_issuer.address,
            asset=MPTCurrency(mpt_issuance_id=MPT_ISSUANCE_ID),
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
            amount=MPTAmount(mpt_issuance_id=MPT_ISSUANCE_ID, value="100"),
        )
        response = await sign_and_reliable_submission_async(
            tx, depositor_wallet, client
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # Step-5: The Loan Broker and Borrower create a Loan object with a LoanSet
        # transaction and the requested principal (excluding fees) is transferred to
        # the Borrower.
        loan_issuer_signed_txn = await autofill_and_sign(
            LoanSet(
                account=loan_issuer.address,
                loan_broker_id=LOAN_BROKER_ID,
                principal_requested="100",
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

        # Wait for the validation of the latest ledger
        await client.request(LEDGER_ACCEPT_REQUEST)

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
            amount=MPTAmount(mpt_issuance_id=MPT_ISSUANCE_ID, value="100"),
        )
        response = await sign_and_reliable_submission_async(tx, borrower_wallet, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")
