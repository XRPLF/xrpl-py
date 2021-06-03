XRPL Async Methods
==================

The `xrpl-py` library supports `Python's asyncio implementation <https://docs.python.org/3/library/asyncio.html>`_. All of these methods are analogous to the synchronous ones.

If working with asynchronous code, **do not** use synchronous methods. Due to the way that loops are handled, this will not work. Each synchronous method has an analogous asynchronous method that should be used instead.

.. toctree::
   :maxdepth: 1
   :titlesonly:

   xrpl.asyncio.account
   xrpl.asyncio.clients
   xrpl.asyncio.ledger
   xrpl.asyncio.transaction
   xrpl.asyncio.wallet
