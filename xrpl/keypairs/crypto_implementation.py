"""
This is just used to allow the ED25519 and SECP256K1 modules to have a
shared type.
"""
from abc import ABC, abstractmethod
from typing import Tuple


class CryptoImplementation(ABC):
    """
    This is just used to allow the ED25519 and SECP256K1 modules to have a
    shared type and interface.
    """

    @staticmethod
    @abstractmethod
    def derive_keypair(
        decoded_seed: bytes,
        is_validator: bool,
    ) -> Tuple[str, str]:  # noqa: D102
        pass

    @staticmethod
    @abstractmethod
    def sign(message: bytes, private_key: str) -> bytes:  # noqa: D102
        pass

    @staticmethod
    @abstractmethod
    def is_valid_message(
        message: bytes, signature: bytes, public_key: str
    ) -> bool:  # noqa: D102
        pass
