.. xrpl-py documentation master file, created by
   sphinx-quickstart on Mon Feb  8 13:40:11 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to xrpl-py's Documentation!
===================================

A pure Python implementation for interacting with the XRP Ledger, the ``xrpl-py`` library simplifies the hardest parts of XRP Ledger interaction, like serialization and transaction signing, by providing native Python methods and models for `XRP Ledger transactions <https://xrpl.org/transaction-formats.html>`_ and core server `API <https://xrpl.org/api-conventions.html>`_ (`rippled <https://github.com/ripple/rippled>`_) objects.


See the `project README <https://github.com/XRPLF/xrpl-py/blob/main/README.md>`_ for more information about its features and usage examples.



Install
--------------
First, ensure that you have `Python 3.8 <https://www.python.org/downloads/>`_ or later.

Then, download the package via ``pip``:

``pip3 install xrpl-py``

Report Issues
--------------

If you run into any bugs or other problems with the library, please report them as issues in the `xrpl-py repo <https://github.com/XRPLF/xrpl-py/issues>`_.

.. toctree::
   :maxdepth: 1
   :caption: Table of Contents

   source/snippets
   source/xrpl.account
   source/xrpl.ledger
   source/xrpl.transaction
   source/xrpl.wallet
   source/xrpl.clients
   source/xrpl.models
   source/xrpl.utils
   source/xrpl
   source/xrpl.core
   source/xrpl.asyncio


Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
