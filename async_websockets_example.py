# flake8: noqa
# not to be merged - just here for collaborative experimentation

import asyncio
import random
import time

from xrpl.asyncio.clients import AsyncWebsocketClient
from xrpl.asyncio.ledger import get_fee
from xrpl.models.requests import StreamParameter, Subscribe


async def consumer(client, index):
    async for message in client:
        print(f"Consumer {index} got {message}")
        rand_millis = random.randint(1, 5000) / 1000
        await asyncio.sleep(rand_millis)


async def main():
    start = time.time()
    print(f"starting main program")
    url = "wss://s.altnet.rippletest.net/"
    async with AsyncWebsocketClient(url) as client:
        asyncio.create_task(consumer(client, 1))
        asyncio.create_task(consumer(client, 2))
        _, fee = await asyncio.gather(
            client.send(Subscribe(streams=[StreamParameter.LEDGER])),
            get_fee(client),
        )
        print(f"FEE!: {fee}")
        await asyncio.sleep(10)

    print(f"stopping main program: took {time.time() - start} seconds")


if __name__ == "__main__":
    asyncio.run(main())
