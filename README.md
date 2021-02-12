# xrpl-py

<<<<<<< HEAD
Supports Python 3.7 and later.
=======
A pure Python implementation of the core functionality necessary to interact with the XRPL Ledger. This library supports the difficult tasks of XRPL serialization and transaction signing, and provides useful native Python models for XRP Ledger objects and `rippled` request and response objects.
>>>>>>> 8fe840a... first crack

# Installation

When it is released, this package will be available to be installed via `pip`. It supports Python 3.5 and later.

# Features

TBD

# Usage

TBD

<<<<<<< HEAD
```bash
pip install pre-commit
pre-commit install
```
=======
# Documentation
>>>>>>> 8fe840a... first crack

In progress, will be linked/discussed here.

# Contributing

We have collected notes on how to contribute to this project in [CONTRIBUTING.md].

[CONTRIBUTING.md]: CONTRIBUTING.md

<<<<<<< HEAD
```bash
poetry run nox -rs tests
```

## Running integration tests

Integration tests are expensive and often flaky. As a result, they don't run
by default with the above command. You'll need to currently run integration
tests manually for each package like so:

```bash
poetry run python -m unittest discover tests.integration.transactions
```

or

```bash
poetry run python -m unittest discover tests.integration.reliable_submission
```

### Generating Documentation

From the `docs` folder,

```bash
poetry run sphinx-apidoc -o source/ ../xrpl
poetry run make html
```

Sphinx generated docs will be in `docs/_build`.
=======
# License

????
>>>>>>> 8fe840a... first crack
