"""The noxfile for xrpl-py."""
import nox
from nox.sessions import Session


@nox.session(python=["3.9", "3.8", "3.7"])
def tests(session: Session) -> None:
    """
    Runs the test suite in xrpl-py.

    You can run individual tests with `nox -rs tests -- <directory or module>`.
    """
    args = session.posargs or ["discover", "tests"]
    session.run("poetry", "install", external=True)
    session.run("python", "-m", "unittest", *args)
