"""The noxfile for xrpl-py."""
import nox


@nox.session(python=["3.9"])
def tests(session):
    """
    Runs the test suite in xrpl-py.

    You can run individual tests with `nox -rs tests -- <directory or module>`.
    """
    args = session.posargs or ["discover", "tests"]
    session.run("poetry", "install", external=True)
    session.run("python", "-m", "unittest", *args)
