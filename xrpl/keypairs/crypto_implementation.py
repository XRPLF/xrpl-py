"""
This is just used to allow the ED25519 and SECP256K1 modules to have a
shared type.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Tuple


class CryptoImplementation(ABC):
    """
    This is just used to allow the ED25519 and SECP256K1 modules to have a
    shared type and interface.
    """

    @classmethod
    @abstractmethod
    def derive_keypair(
        cls: CryptoImplementation,
        decoded_seed: bytes,
        is_validator: bool,
    ) -> Tuple[str, str]:  # noqa: D102
        ...

    @classmethod
    @abstractmethod
    def sign(
        cls: CryptoImplementation, message: str, private_key: str
    ) -> bytes:  # noqa: D102
        ...

    @classmethod
    @abstractmethod
    def is_valid_message(
        cls: CryptoImplementation, message: str, signature: bytes, public_key: str
    ) -> bool:  # noqa: D102
        ...
