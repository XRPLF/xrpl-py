"""Public interface for XRPL keypairs implementation."""
from xrpl.keypairs.main import derive, generate_seed

__all__ = [
    derive,
    generate_seed,
]
