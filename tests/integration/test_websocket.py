from unittest import TestCase

from xrpl.clients import WebsocketClient
from xrpl.ledger import get_fee

# ACCOUNT = WALLET.classic_address

# CLEAR_FLAG = 3
# DOMAIN = "6578616D706C652E636F6D".lower()
# EMAIL_HASH = "10000000002000000000300000000012"
# MESSAGE_KEY = "03AB40A0490F9B7ED8DF29D246BF2D6269820A0EE7742ACDD457BEA7C7D0931EDB"
# SET_FLAG = 8
# TRANSFER_RATE = 0
# TICK_SIZE = 10

WEBSOCKET_CLIENT = WebsocketClient("wss://s.altnet.rippletest.net/")


class TestWebsocket(TestCase):
    def test_get_fee(self):
        print(get_fee(WEBSOCKET_CLIENT))

    # def test_required_fields_and_set_flag(self):
    #     account_set = AccountSet(
    #         account=ACCOUNT,
    #         sequence=WALLET.sequence,
    #         set_flag=SET_FLAG,
    #     )
    #     signed_tx = safe_sign_and_autofill_transaction(account_set, WALLET,
    # WEBSOCKET_CLIENT)
    #     return send_reliable_submission(signed_tx, client)
    #     WALLET.sequence += 1
