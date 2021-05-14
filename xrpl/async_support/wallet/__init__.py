"""Top-level exports for async wallet generation."""
from xrpl.async_support.wallet.wallet_generation import (
    XRPLFaucetException,
    generate_faucet_wallet,
)

__all__ = ["XRPLFaucetException", "generate_faucet_wallet"]
