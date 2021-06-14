"""The noxfile for xrpl-py."""
# import nox
import nox_poetry.patch  # noqa: F401
from nox.sessions import Session


@nox_poetry.session(python=["3.9", "3.8", "3.7"])
def unit_tests(session: Session) -> None:
    """
    Runs the unit test suite in xrpl-py.

    You can run individual tests with
    `nox -rs unit_tests -- <directory or module>`.
    """
    args = session.posargs or ["discover", "tests/unit"]
    session.install(".")
    session.run("python", "-m", "unittest", *args)


@nox_poetry.session(python=["3.9", "3.8", "3.7"])
def integration_tests(session: Session) -> None:
    """
    Runs the integration test suite in xrpl-py.

    You can run individual tests with
    `nox -rs integration_tests -- <directory or module>`.
    """
    args = session.posargs or ["discover", "tests/integration"]
    session.install(".")
    session.run("python", "-m", "unittest", *args)
