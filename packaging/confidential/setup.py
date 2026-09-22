# Minimal setup.py: PEP 621 metadata lives in pyproject.toml, but cffi's
# setuptools integration (`cffi_modules`) must be passed to setup(). This wires
# the CFFI extension build into the normal wheel build that cibuildwheel drives.
#
# The path is relative to this project dir and resolves after the source is
# staged here by scripts/stage-source.sh. `build_mpt_crypto.py` exposes a
# module-level `ffibuilder` whose set_source() #includes the real mpt-crypto
# headers, so the C compiler validates every cdef signature against the library
# ABI at build time.
from setuptools import setup

setup(
    cffi_modules=["xrpl/ext/confidential/build_mpt_crypto.py:ffibuilder"],
)
