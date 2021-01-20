# xrpl-py

Supports Python 3.5 and later.

## Contributing

### Setting up the dev environment

Install poetry per the instructions at https://python-poetry.org/docs/

```bash
poetry install
```

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

### Installing Dependencies

```bash
python setup.py develop
```

### Running Tests

```bash
python -m unittest discover tests
```
