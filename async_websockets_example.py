# flake8: noqa
# not to be merged - just here for collaborative experimentation

import asyncio
import random
import time

from xrpl.asyncio.clients import AsyncWebsocketClient
from xrpl.asyncio.ledger import get_fee
from xrpl.models.requests import StreamParameter, Subscribe

MSGS = []


async def consumer(client):
    async for message in client:
        MSGS.append(message)
        print(f"Got {message}")
        rand_millis = random.randint(1, 5000) / 1000
        await asyncio.sleep(rand_millis)


async def main():
    start = time.time()
    print(f"starting main program")
    url = "wss://s.altnet.rippletest.net/"

    # open client
    async with AsyncWebsocketClient(url) as client:
        # example usage of sugar
        fee = await get_fee(client)
        print(f"FEE!: {fee}")

        # set up subscription
        asyncio.create_task(client.send(Subscribe(streams=[StreamParameter.LEDGER])))

        # set up a listener task
        # (you could do exactly what is done in the sync example
        # if you wanted, but that would not show the benefits of async)
        asyncio.create_task(consumer(client))

        # after 10 secs close the client
        await asyncio.sleep(10)

    print(
        f"stopping main program: took {time.time() - start} seconds\nRead {len(MSGS)} msgs"
    )


if __name__ == "__main__":
    asyncio.run(main())
