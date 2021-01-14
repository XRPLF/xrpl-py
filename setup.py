from setuptools import setup

setup(
    name="xrpl",
    version="0.1",
    description="Foundational XRPL ledger tools",
    url="https://github.com/xpring-eng/xrpl-py",
    # seriously - TODO
    license="TODO",
    packages=["xrpl"],
    install_requires=[
        "base58",
        "ECPy",
    ],
    zip_safe=False,
)
