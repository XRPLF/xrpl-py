from tests.integration.it_utils import JSON_RPC_CLIENT, sign_and_reliable_submission
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.transactions import OfferCreate, PaymentChannelCreate
from xrpl.wallet import generate_faucet_wallet

WALLET = generate_faucet_wallet(JSON_RPC_CLIENT)
DESTINATION = generate_faucet_wallet(JSON_RPC_CLIENT)
OFFER = sign_and_reliable_submission(
    OfferCreate(
        account=WALLET.classic_address,
        sequence=WALLET.next_sequence_num,
        taker_gets="13100000",
        taker_pays=IssuedCurrencyAmount(
            currency="USD",
            issuer=WALLET.classic_address,
            value="10",
        ),
    ),
    WALLET,
)
WALLET.next_sequence_num += 1
PAYMENT_CHANNEL = sign_and_reliable_submission(
    PaymentChannelCreate(
        account=WALLET.classic_address,
        sequence=WALLET.next_sequence_num,
        amount="1",
        destination=DESTINATION.classic_address,
        settle_delay=86400,
        public_key=WALLET.public_key,
    ),
    WALLET,
)
WALLET.next_sequence_num += 1
