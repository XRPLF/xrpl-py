import subprocess

def run_unit_tests():   
    """
    Run all unittests. Equivalent to:
    `poetry run python -u -m unittest discover tests/unit`
    """
    subprocess.run(
        ['python', '-u', '-m', 'unittest', 'discover', 'tests/unit']
    )

def run_integration_tests():   
    """
    Run all integration tests. Equivalent to:
    `poetry run python -u -m unittest discover tests/integration`
    """
    subprocess.run(
        ['python', '-u', '-m', 'unittest', 'discover', 'tests/integration']
    )