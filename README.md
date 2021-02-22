# xrpl-py

Supports Python 3.5 and later.

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

### Generating Documentation

From the `docs` folder,

```bash
poetry run sphinx-apidoc -o source/ ../xrpl
make html
```

Sphinx generated docs will be in `docs/_build`.
