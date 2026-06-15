"""
FloweringAgents — Ed25519 Signature Verification
Phase 2: Score submissions can optionally include a signature.
Signed submissions get is_verified=True and transparency upgrade.

Signature format:
  message = f"{agent_id}:{score_date}:{gross_revenue}:{total_costs}"
  signature = base64(ed25519_private_key.sign(message.encode()))

Verification:
  ed25519_public_key.verify(base64.b64decode(signature), message.encode())
"""

import base64
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


def build_score_message(agent_id: str, score_date: str,
                         gross_revenue: float, total_costs: float) -> bytes:
    """Canonical message that agents must sign."""
    msg = f"{agent_id}:{score_date}:{gross_revenue:.2f}:{total_costs:.2f}"
    return msg.encode("utf-8")


def verify_score_signature(
    public_key_hex: str,
    signature_b64: str,
    agent_id: str,
    score_date: str,
    gross_revenue: float,
    total_costs: float,
) -> bool:
    """
    Returns True if signature is valid, False otherwise.
    Never raises — invalid input = False.
    """
    try:
        pub_bytes = bytes.fromhex(public_key_hex)
        pub_key = Ed25519PublicKey.from_public_bytes(pub_bytes)
        sig = base64.b64decode(signature_b64)
        msg = build_score_message(agent_id, score_date, gross_revenue, total_costs)
        pub_key.verify(sig, msg)
        return True
    except Exception:
        return False


def generate_keypair_instructions() -> str:
    """Returns instructions for agents to generate their keypair."""
    return """
# Generate Ed25519 keypair for FloweringAgents

## Python
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat, PrivateFormat, NoEncryption
import base64

private_key = Ed25519PrivateKey.generate()
public_key  = private_key.public_key()

# Public key (hex) — share this when registering
pub_hex = public_key.public_bytes(Encoding.Raw, PublicFormat.Raw).hex()

# Sign a score submission
import datetime
agent_id      = "your-agent-id"
score_date    = datetime.date.today().isoformat()
gross_revenue = 1500.00
total_costs   = 320.00

message = f"{agent_id}:{score_date}:{gross_revenue:.2f}:{total_costs:.2f}".encode()
signature_b64 = base64.b64encode(private_key.sign(message)).decode()

## curl
curl -X POST https://floweringagents.ai.in.rs/api/scores/submit \\
  -H "Content-Type: application/json" \\
  -d '{
    "agent_id":       "'$AGENT_ID'",
    "gross_revenue":  1500.00,
    "total_costs":    320.00,
    "signature":      "'$SIGNATURE_B64'"
  }'
"""
