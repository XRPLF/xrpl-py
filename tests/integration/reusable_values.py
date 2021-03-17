from tests.integration.it_utils import JSON_RPC_CLIENT
from xrpl.account import get_fee
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.transactions import OfferCreate, PaymentChannelCreate
from xrpl.transaction import send_reliable_submission
from xrpl.wallet import generate_faucet_wallet

WALLET = generate_faucet_wallet(JSON_RPC_CLIENT)
DESTINATION = generate_faucet_wallet(JSON_RPC_CLIENT)
FEE = get_fee(JSON_RPC_CLIENT)
OFFER = send_reliable_submission(
    OfferCreate(
        account=WALLET.classic_address,
        fee=FEE,
        taker_gets="13100000",
        taker_pays=IssuedCurrencyAmount(
            currency="USD",
            issuer=WALLET.classic_address,
            value="10",
        ),
        sequence=WALLET.next_sequence_num,
        last_ledger_sequence=WALLET.next_sequence_num + 10,
    ),
    WALLET,
    JSON_RPC_CLIENT,
)
PAYMENT_CHANNEL = send_reliable_submission(
    PaymentChannelCreate(
        account=WALLET.classic_address,
        sequence=WALLET.next_sequence_num,
        last_ledger_sequence=WALLET.next_sequence_num + 10,
        fee=FEE,
        amount="1",
        destination=DESTINATION.classic_address,
        settle_delay=86400,
        public_key=WALLET.pub_key,
    ),
    WALLET,
    JSON_RPC_CLIENT,
)
