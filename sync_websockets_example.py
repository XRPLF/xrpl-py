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
    with WebsocketClient(url, onmessage) as client:
        client.send(Subscribe(streams=[StreamParameter.LEDGER]))
        fee = get_fee(client)
        print(f"FEE!: {fee}")
        time.sleep(10)

    print(f"stopping main program: took {time.time() - start} seconds")


if __name__ == "__main__":
    main()
