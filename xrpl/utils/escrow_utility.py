from cryptoconditions import PreimageSha256

def generate_escrow_cryptoconditions(secret: bytes) -> dict:
    """Generate a condition and fulfillment for escrows"""
    fufill = PreimageSha256(preimage=secret)
    return {
    "condition": str.upper(fufill.condition_binary.hex()),
    "fulfillment": str.upper(fufill.serialize_binary().hex())}
