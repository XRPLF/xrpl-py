"""
Abstract base class for cryptographic algorithms in the XRP Ledger. The classes
for all cryptographic algorithms are derived from this interface.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Tuple, Type

from ecpy.keys import ECPrivateKey  # type: ignore


class CryptoImplementation(ABC):
    """
    Abstract base class for cryptographic algorithms in the XRP Ledger. The
    classes for all cryptographic algorithms are derived from this interface.
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
