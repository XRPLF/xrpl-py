from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    accept_ledger_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import DESTINATION as DESTINATION_WALLET
from tests.integration.reusable_values import WALLET
from xrpl.asyncio.ledger import get_fee, get_latest_validated_ledger_sequence
from xrpl.asyncio.transaction import (
    XRPLReliableSubmissionException,
    _calculate_fee_per_transaction_type,
    autofill,
    autofill_and_sign,
    sign,
    sign_and_submit,
    simulate,
)
from xrpl.asyncio.transaction import submit as submit_transaction_alias_async
from xrpl.asyncio.transaction import submit_and_wait
from xrpl.clients import XRPLRequestFailureException
from xrpl.core.addresscodec import classic_address_to_xaddress
from xrpl.core.binarycodec.main import encode
from xrpl.models.amounts.issued_currency_amount import IssuedCurrencyAmount
from xrpl.models.exceptions import XRPLException
from xrpl.models.requests import ServerState, Tx
from xrpl.models.transactions import AccountDelete, AccountSet, EscrowFinish, Payment
from xrpl.utils import xrp_to_drops

ACCOUNT = WALLET.address
DESTINATION = DESTINATION_WALLET.address

CLEAR_FLAG = 3
DOMAIN = "6578616D706C652E636F6D".lower()
EMAIL_HASH = "10000000002000000000300000000012"
MESSAGE_KEY = "03AB40A0490F9B7ED8DF29D246BF2D6269820A0EE7742ACDD457BEA7C7D0931EDB"
SET_FLAG = 8
TRANSFER_RATE = 0
TICK_SIZE = 10
FEE = xrp_to_drops(60)  # standalone has a delete fee of 50 XRP
DESTINATION_TAG = 3
OFFER_SEQUENCE = 7
CONDITION = (
    "A0258020E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855810100"
)
FULFILLMENT = "A0028000"
OWNER = "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn"


class TestTransaction(IntegrationTestCase):
    @test_async_and_sync(
        globals(),
    )
    async def test_none_as_destination_tag(self, client):
        # GIVEN a new transaction (payment)
        payment_transaction = Payment(
            account=WALLET.address,
            amount="100",
            destination=classic_address_to_xaddress(DESTINATION, None, False),
        )

        # WHEN we sign locally, autofill, and submit the transaction
        response = await sign_and_reliable_submission_async(
            payment_transaction, WALLET, client
        )
        payment_hash = response.result["tx_json"]["hash"]
        payment_ledger_index = response.result["validated_ledger_index"]

        # THEN we expect to retrieve this transaction from its hash with
        # min_ledger and max_ledger parameters
        payment = await client.request(
            Tx(
                transaction=payment_hash,
                min_ledger=payment_ledger_index - 5,
                max_ledger=payment_ledger_index + 5,
            )
        )

        # AND we expect the result Account to be the same as the original payment Acct
        self.assertEqual(payment.result["tx_json"]["Account"], ACCOUNT)
        # AND we expect the response to be successful (200)
        self.assertTrue(payment.is_successful())

    @test_async_and_sync(globals())
    async def test_high_fee_account_delete_unauthorized(self, client):
        # GIVEN a new AccountDelete transaction
        account_delete = AccountDelete(
            account=ACCOUNT,
            # WITH fee higher than 2 XRP
            fee=FEE,
            destination=DESTINATION,
            destination_tag=DESTINATION_TAG,
        )
        # We expect an XRPLException to be raised
        with self.assertRaises(XRPLException):
            await sign_and_reliable_submission_async(account_delete, WALLET, client)

    @test_async_and_sync(globals())
    async def test_high_fee_account_set_unauthorized(self, client):
        # GIVEN a new AccountSet transaction
        account_set = AccountSet(
            account=ACCOUNT,
            clear_flag=CLEAR_FLAG,
            domain=DOMAIN,
            email_hash=EMAIL_HASH,
            message_key=MESSAGE_KEY,
            transfer_rate=TRANSFER_RATE,
            tick_size=TICK_SIZE,
            # WITH fee higher than 2 XRP
            fee=FEE,
        )
        # We expect an XRPLException to be raised
        with self.assertRaises(XRPLException):
            await sign_and_reliable_submission_async(account_set, WALLET, client)

    @test_async_and_sync(globals())
    async def test_payment_high_fee_authorized(self, client):
        # GIVEN a new Payment transaction
        response = await sign_and_reliable_submission_async(
            Payment(
                account=WALLET.address,
                amount="1",
                # WITH the fee higher than 2 XRP
                fee=FEE,
                destination=DESTINATION,
            ),
            WALLET,
            client,
            # WITHOUT checking the fee value
            check_fee=False,
        )
        # THEN we expect the transaction to be successful
        self.assertTrue(response.is_successful())

    @test_async_and_sync(
        globals(),
        [
            "xrpl.transaction.autofill_and_sign",
            "xrpl.transaction.submit",
        ],
    )
    async def test_payment_high_fee_authorized_with_submit_alias(self, client):
        signed_and_autofilled = await autofill_and_sign(
            Payment(
                account=WALLET.address,
                amount="1",
                fee=FEE,
                destination=DESTINATION,
            ),
            client,
            WALLET,
            check_fee=False,
        )

        response = await submit_transaction_alias_async(signed_and_autofilled, client)
        self.assertTrue(response.is_successful())

    @test_async_and_sync(globals(), ["xrpl.transaction.autofill"])
    async def test_calculate_account_delete_fee(self, client):
        # GIVEN a new AccountDelete transaction
        account_delete = AccountDelete(
            account=ACCOUNT,
            destination=DESTINATION,
            destination_tag=DESTINATION_TAG,
        )

        # AFTER autofilling the transaction fee
        account_delete_autofilled = await autofill(account_delete, client)

        # THEN we expect the calculated fee to be 50 XRP (default in standalone)
        server_state = await client.request(ServerState())
        expected_fee = str(
            server_state.result["state"]["validated_ledger"]["reserve_inc"]
        )
        self.assertEqual(account_delete_autofilled.fee, expected_fee)

    @test_async_and_sync(
        globals(),
        ["xrpl.transaction.autofill", "xrpl.ledger.get_fee"],
    )
    async def test_calculate_escrow_finish_fee(self, client):
        # GIVEN a new EscrowFinish transaction
        escrow_finish = EscrowFinish(
            account=ACCOUNT,
            owner=OWNER,
            offer_sequence=OFFER_SEQUENCE,
            condition=CONDITION,
            fulfillment=FULFILLMENT,
        )

        # AFTER autofilling the transaction fee
        escrow_finish_autofilled = await autofill(escrow_finish, client)

        # AND calculating the expected fee with the formula
        # BaseFee × (33 + (Fulfillment size in bytes ÷ 16))
        net_fee = int(await get_fee(client))
        fulfillment_in_bytes = FULFILLMENT.encode("ascii")
        expected_fee = net_fee * (33 + len(fulfillment_in_bytes) / 16)

        # THEN we expect the fee to be the calculation result above
        self.assertEqual(float(escrow_finish_autofilled.fee), float(expected_fee))

    @test_async_and_sync(
        globals(),
        ["xrpl.transaction.autofill", "xrpl.ledger.get_fee"],
    )
    async def test_calculate_payment_fee(self, client):
        # GIVEN a new Payment transaction
        payment = Payment(
            account=WALLET.address,
            amount="100",
            destination=DESTINATION,
        )

        # AFTER autofilling the transaction fee
        payment_autofilled = await autofill(payment, client)

        # THEN We expect the fee to be the default network fee (The transaction cost of
        # a reference transaction, in drops of XRP)
        expected_fee = await get_fee(client)
        self.assertEqual(payment_autofilled.fee, expected_fee)

    @test_async_and_sync(
        globals(),
        ["xrpl.transaction.autofill"],
    )
    async def test_networkid_non_reserved_networks(self, client):
        tx = AccountSet(
            account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
            fee=FEE,
            domain="www.example.com",
        )
        transaction = await autofill(tx, client)

        # Autofill should populate the tx networkID and build_version from 1.11.0 or
        # later. NetworkID field is populated only for networks where network_id > 1024
        self.assertEqual(client.network_id, 63456)
        self.assertEqual(transaction.network_id, 63456)

    @test_async_and_sync(globals(), ["xrpl.transaction.autofill"], use_testnet=True)
    async def test_networkid_reserved_networks(self, client):
        tx = AccountSet(
            account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
            fee=FEE,
            domain="www.example.com",
        )
        # The network_id is less than 1024 for the testnet.
        # Hence network_id field is not set
        transaction = await autofill(tx, client)

        # Although the client network_id property is set,
        # the corresponding field in transaction is not populated
        self.assertIsNone(transaction.network_id)
        self.assertEqual(client.network_id, 1)

    @test_async_and_sync(
        globals(),
        [
            "xrpl.transaction.sign_and_submit",
        ],
    )
    async def test_sign_and_submit(self, client):
        payment_dict = {
            "account": ACCOUNT,
            "fee": "10",
            "amount": "100",
            "destination": DESTINATION,
        }
        payment_transaction = Payment.from_dict(payment_dict)
        response = await sign_and_submit(payment_transaction, client, WALLET)
        self.assertTrue(response.is_successful())

    @test_async_and_sync(globals(), async_only=True)
    async def test_basic_calculate_fee_per_transaction_type(self, client):
        fee = await _calculate_fee_per_transaction_type(
            Payment(
                account="rweYz56rfmQ98cAdRaeTxQS9wVMGnrdsFp",
                amount=IssuedCurrencyAmount(
                    currency="USD",
                    issuer="rweYz56rfmQ98cAdRaeTxQS9wVMGnrdsFp",
                    value="0.0001",
                ),
                destination="rweYz56rfmQ98cAdRaeTxQS9wVMGnrdsFp",
                send_max=IssuedCurrencyAmount(
                    currency="BTC",
                    issuer="rweYz56rfmQ98cAdRaeTxQS9wVMGnrdsFp",
                    value="0.0000002831214446",
                ),
            ),
            client,
        )

        # The expected fee is read from the below-specified config file
        expected_fee = ""
        with open(".ci-config/rippled.cfg", "r", encoding="utf-8") as file:
            lines = file.readlines()  # Read all lines into a list

            for value in lines:
                kv_pairs = value.split()
                # This step assumes that no non-`voting` section in the config file
                # uses the reference_fee key-value pair.
                if "reference_fee" in kv_pairs:
                    expected_fee = kv_pairs[2]
                    break

        self.assertEqual(fee, expected_fee)

    @test_async_and_sync(
        globals(),
        [
            "xrpl.transaction.simulate",
        ],
    )
    async def test_simulate(self, client):
        response = await simulate(AccountSet(account=WALLET.address), client)

        self.assertTrue(response.is_successful())
        self.assertEqual(response.type, "response")
        self.assertIn(
            "meta", response.result, "Key 'meta' not found in simulate response."
        )
        self.assertIsInstance(
            response.result["meta"], dict, "'meta' should be a dictionary."
        )
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")
        self.assertEqual(response.result["engine_result_code"], 0)
        self.assertFalse(response.result["applied"])


class TestSubmitAndWait(IntegrationTestCase):
    @test_async_and_sync(
        globals(),
        [
            "xrpl.transaction.submit_and_wait",
            "xrpl.ledger.get_fee",
        ],
    )
    async def test_submit_and_wait_simple(self, client):
        account_set = AccountSet(
            account=ACCOUNT,
            set_flag=SET_FLAG,
        )
        await accept_ledger_async(delay=1)
        response = await submit_and_wait(account_set, client, WALLET)
        self.assertTrue(response.result["validated"])
        self.assertEqual(response.result["meta"]["TransactionResult"], "tesSUCCESS")
        self.assertTrue(response.is_successful())
        self.assertEqual(response.result["tx_json"]["Fee"], await get_fee(client))

    @test_async_and_sync(
        globals(),
        [
            "xrpl.transaction.submit_and_wait",
            "xrpl.ledger.get_fee",
        ],
    )
    async def test_submit_and_wait_payment(self, client):
        payment_transaction = Payment(
            account=ACCOUNT,
            amount="10",
            destination=DESTINATION,
        )
        await accept_ledger_async(delay=1)
        response = await submit_and_wait(payment_transaction, client, WALLET)
        self.assertTrue(response.result["validated"])
        self.assertEqual(response.result["meta"]["TransactionResult"], "tesSUCCESS")
        self.assertTrue(response.is_successful())
        self.assertEqual(response.result["tx_json"]["Fee"], await get_fee(client))

    @test_async_and_sync(
        globals(),
        [
            "xrpl.transaction.autofill_and_sign",
            "xrpl.transaction.submit_and_wait",
            "xrpl.ledger.get_fee",
        ],
    )
    async def test_submit_and_wait_signed(self, client):
        payment_transaction = Payment(
            account=ACCOUNT,
            amount="10",
            destination=DESTINATION,
        )
        payment_transaction_signed = await autofill_and_sign(
            payment_transaction, client, WALLET
        )
        await accept_ledger_async(delay=1)
        response = await submit_and_wait(payment_transaction_signed, client)
        self.assertTrue(response.result["validated"])
        self.assertEqual(response.result["meta"]["TransactionResult"], "tesSUCCESS")
        self.assertTrue(response.is_successful())
        self.assertEqual(response.result["tx_json"]["Fee"], await get_fee(client))

    @test_async_and_sync(
        globals(),
        [
            "xrpl.transaction.autofill_and_sign",
            "xrpl.transaction.submit_and_wait",
            "xrpl.ledger.get_fee",
        ],
    )
    async def test_submit_and_wait_blob(self, client):
        payment_transaction = Payment(
            account=ACCOUNT,
            amount="10",
            destination=DESTINATION,
        )
        payment_transaction_signed = await autofill_and_sign(
            payment_transaction, client, WALLET
        )
        await accept_ledger_async(delay=1)
        payment_transaction_signed_blob = encode(payment_transaction_signed.to_xrpl())
        response = await submit_and_wait(payment_transaction_signed_blob, client)
        self.assertTrue(response.result["validated"])
        self.assertEqual(response.result["meta"]["TransactionResult"], "tesSUCCESS")
        self.assertTrue(response.is_successful())
        self.assertEqual(response.result["tx_json"]["Fee"], await get_fee(client))

    @test_async_and_sync(
        globals(),
        [
            "xrpl.transaction.submit_and_wait",
            "xrpl.ledger.get_latest_validated_ledger_sequence",
        ],
    )
    async def test_submit_and_wait_last_ledger_expiration(self, client):
        payment_transaction = Payment(
            account=ACCOUNT,
            last_ledger_sequence=await get_latest_validated_ledger_sequence(client),
            amount="100",
            destination=DESTINATION,
        )
        await accept_ledger_async(delay=1)
        with self.assertRaises(XRPLReliableSubmissionException):
            await submit_and_wait(payment_transaction, client, WALLET)

    @test_async_and_sync(
        globals(),
        [
            "xrpl.transaction.submit_and_wait",
        ],
    )
    async def test_submit_and_wait_tec_error(self, client):
        payment_transaction = Payment(
            account=ACCOUNT,
            amount=xrp_to_drops(10**10),  # tecINSUFFICIENT_FUNDS
            destination=DESTINATION,
        )
        await accept_ledger_async(delay=1)
        with self.assertRaises(XRPLReliableSubmissionException):
            await submit_and_wait(payment_transaction, client, WALLET)

    @test_async_and_sync(
        globals(),
        [
            "xrpl.transaction.sign",
            "xrpl.transaction.submit_and_wait",
            "xrpl.ledger.get_latest_validated_ledger_sequence",
        ],
    )
    async def test_submit_and_wait_bad_transaction(self, client):
        payment_dict = {
            "account": ACCOUNT,
            "fee": "10",
            "last_ledger_sequence": await get_latest_validated_ledger_sequence(client)
            + 20,
            "amount": "100",
            "destination": DESTINATION,
        }
        payment_transaction = Payment.from_dict(payment_dict)
        signed_payment_transaction = sign(payment_transaction, WALLET)
        with self.assertRaises(XRPLRequestFailureException):
            await submit_and_wait(signed_payment_transaction, client)

    @test_async_and_sync(
        globals(),
        [
            "xrpl.transaction.sign",
            "xrpl.transaction.submit_and_wait",
            "xrpl.account.get_next_valid_seq_number",
        ],
    )
    async def test_reliable_submission_no_last_ledger_sequence(self, client):
        payment_dict = {
            "account": ACCOUNT,
            "fee": "10",
            "amount": "100",
            "destination": DESTINATION,
        }
        payment_transaction = Payment.from_dict(payment_dict)
        signed_payment_transaction = sign(payment_transaction, WALLET)
        with self.assertRaises(XRPLReliableSubmissionException):
            await submit_and_wait(signed_payment_transaction, client)
