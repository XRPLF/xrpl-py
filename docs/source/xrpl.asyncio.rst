Async Support
===================

The `xrpl-py` library supports `Python's asyncio implementation <https://docs.python.org/3/library/asyncio.html>`_. All of these methods are equivalent to the synchronous ones.

Due to the way that `asyncio` event loops are handled, you cannot call synchronous methods from asynchronous code. Each synchronous method has an equivalent asynchronous method in this module that should be used instead.

.. toctree::
   :maxdepth: 1
   :titlesonly:

   xrpl.asyncio.account
   xrpl.asyncio.ledger
   xrpl.asyncio.transaction
   xrpl.asyncio.wallet
   xrpl.asyncio.clients
