# flake8: noqa
# not to be merged - just here for collaborative experimentation

import random
import time

from xrpl.clients.websocket_client import WebsocketClient
from xrpl.ledger import get_fee
from xrpl.models.requests import StreamParameter, Subscribe


def onmessage(message):
    print(f"Got {message}")
    rand_millis = random.randint(1, 5000) / 1000
    time.sleep(rand_millis)


def main():
    start = time.time()
    print("starting main program")
    url = "wss://s.altnet.rippletest.net/"
    msg_count = 0

    # open client
    with WebsocketClient(url) as client:
        # example usage of sugar
        fee = get_fee(client)
        print(f"FEE!: {fee}")

        # set up subscription
        client.send(Subscribe(streams=[StreamParameter.LEDGER]))

        # example of reading 10 messages from the socket
        # and processing them. each iteration here will block waiting for a
        # message.
        for message in client:
            msg_count += 1
            onmessage(message)
            if msg_count > 10:
                break

    print(f"stopping main program: took {time.time() - start} seconds")


if __name__ == "__main__":
    main()
