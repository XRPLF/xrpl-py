# xrpl-py

Supports Python 3.5 and later.

## Contributing
### Setting up the dev environment

```bash
# Create a new virtual environment.
python -m venv venv

# Activate the virtual environment.
venv/bin/activate.

# Install dev dependencies into virtual environment.
python -m pip install -r requirements-dev.txt
```

### Linting

After setting up the dev environment using the commands above, you can run the linter
by executing

```bash
flake8 ./xrpl
```

### Installing Dependencies
```bash
python setup.py develop
```

### Running Tests
```bash
python -m unittest discover tests
```
