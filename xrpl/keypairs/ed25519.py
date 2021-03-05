"""Methods for deriving keypairs given an ED25519-encoded seed."""
from __future__ import annotations

from hashlib import sha512
from typing import Tuple, Type, cast

from ecpy.curves import Curve  # type: ignore
from ecpy.eddsa import EDDSA  # type: ignore
from ecpy.keys import ECPrivateKey, ECPublicKey  # type: ignore
from typing_extensions import Final

from xrpl.keypairs.crypto_implementation import CryptoImplementation
from xrpl.keypairs.exceptions import XRPLKeypairsException
from xrpl.keypairs.helpers import sha512_first_half

PREFIX: Final[str] = "ED"
_CURVE: Final[Curve] = Curve.get_curve("Ed25519")
_SIGNER: Final[EDDSA] = EDDSA(sha512)


class ED25519(CryptoImplementation):
    """Methods for deriving keypairs given an ED25519-encoded seed."""

    @classmethod
    def derive_keypair(
        cls: Type[ED25519], decoded_seed: bytes, is_validator: bool
    ) -> Tuple[str, str]:
        """
        Derives a keypair.

        Args:
            decoded_seed: an ED25519 seed from which to derive keypair.
            is_validator: if True indicates that caller wishes to derive a validator
                keypair from this seed, however, that is always invalid for this
                algorithm and will cause this function to raise.

        Returns:
            A (private key, public key) derived from seed

        Raises:
            XRPLKeypairsException: If the keypair is a validator keypair.
        """
        if is_validator:
            raise XRPLKeypairsException("validator keypairs cannot use ED25519")

        raw_private = sha512_first_half(decoded_seed)
        private = ECPrivateKey(int.from_bytes(raw_private, "big"), _CURVE)
        public = EDDSA.get_public_key(private, sha512)
        return (
            cls._format_key(cls._public_key_to_str(public)),
            cls._format_key(cls._private_key_to_str(private)),
        )

    @classmethod
    def sign(cls: Type[ED25519], message: str, private_key: str) -> bytes:
        """
        Signs a message.

        Args:
            message: Message to sign
            private_key: Key with which to sign message

        Returns:
            The signature of message signed using private_key.
        """
        raw_private = private_key[len(PREFIX) :]
        wrapped_private = ECPrivateKey(int(raw_private, 16), _CURVE)
        return cast(bytes, _SIGNER.sign(message, wrapped_private))

    @classmethod
    def is_valid_message(
        cls: Type[ED25519], message: str, signature: bytes, public_key: str
    ) -> bool:
        """
        Checks whether or not a message is valid.

        Args:
            message: Message to check against signature
            signature: Signature of message to to verify
            public_key: Public key corresponding to private key used to
                generate signature

        Returns:
            Whether message is valid given signature and public_key

        """
        raw_public = public_key[len(PREFIX) :]
        public_key_point = _CURVE.decode_point(bytes.fromhex(raw_public))
        wrapped_public = ECPublicKey(public_key_point)
        return cast(bool, _SIGNER.verify(message, signature, wrapped_public))

    @classmethod
    def _public_key_to_str(cls: Type[ED25519], key: ECPublicKey) -> str:
        return cast(str, _CURVE.encode_point(key.W).hex())

    @classmethod
    def _private_key_to_str(cls: Type[ED25519], key: ECPrivateKey) -> str:
        return format(key.d, "x")

    @classmethod
    def _format_key(cls: Type[ED25519], keystr: str) -> str:
        return (PREFIX + keystr).upper()
