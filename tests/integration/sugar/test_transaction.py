from unittest import TestCase

from tests.integration.it_utils import JSON_RPC_CLIENT

# from tests.integration.reusable_values import FEE
# from xrpl.models.transactions import Payment
# from xrpl.transaction import send_reliable_submission
from xrpl.wallet import Wallet, generate_faucet_wallet

NEW_WALLET = generate_faucet_wallet(JSON_RPC_CLIENT)
EMPTY_WALLET = Wallet.generate_seed_and_wallet()


class TestTransaction(TestCase):
    pass
