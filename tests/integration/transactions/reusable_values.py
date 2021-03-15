from tests.integration.it_utils import JSON_RPC_CLIENT
from xrpl.account import get_fee
from xrpl.wallet import generate_faucet_wallet

WALLET = generate_faucet_wallet(JSON_RPC_CLIENT)
FEE = get_fee(JSON_RPC_CLIENT)
