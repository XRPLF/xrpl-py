[![Documentation Status](https://readthedocs.org/projects/xrpl-py/badge)](https://xrpl-py.readthedocs.io/)

# xrpl-py

Supports Python 3.7 and later.

## Contributing

### Setting up the dev environment

Install poetry per the instructions at https://python-poetry.org/docs/

```bash
poetry install
```

This will install dev and library dependencies.

Install pre-commit globally to get access to the pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

### Linting

After setting up the dev environment using the commands above, you can run the linter
by executing

```bash
poetry run flake8 ./xrpl
```

### Running Tests

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
