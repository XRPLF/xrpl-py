"""
This is just used to allow the ED25519 and SECP256K1 modules to have a
shared type.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Tuple, Type

from ecpy.keys import ECPrivateKey  # type: ignore


class CryptoImplementation(ABC):
    """
    This is just used to allow the ED25519 and SECP256K1 modules to have a
    shared type and interface.
    """

    @classmethod
    @abstractmethod
    def derive_keypair(
        cls: Type[CryptoImplementation],
        decoded_seed: bytes,
        is_validator: bool,
    ) -> Tuple[str, str]:  # noqa: D102
        pass

    @classmethod
    @abstractmethod
    def sign(
        cls: Type[CryptoImplementation],
        message: bytes,
        private_key: str,
    ) -> bytes:  # noqa: D102
        pass

    @classmethod
    @abstractmethod
    def is_valid_message(
        cls: Type[CryptoImplementation],
        message: bytes,
        signature: bytes,
        public_key: str,
    ) -> bool:  # noqa: D102
        pass

    @classmethod
    def _private_key_to_str(cls: Type[CryptoImplementation], key: ECPrivateKey) -> str:
        return format(key.d, "x")
