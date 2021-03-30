"""Top-level exports for the wallet generation package."""
from xrpl.wallet.main import Wallet
from xrpl.wallet.wallet_generation import XRPLFaucetException, generate_faucet_wallet

__all__ = ["Wallet", "generate_faucet_wallet", "XRPLFaucetException"]
