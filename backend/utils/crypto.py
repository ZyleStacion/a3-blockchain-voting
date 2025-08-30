from eth_account import Account
import eth_keys
import eth_utils
from eth_account.messages import encode_defunct
# TODO : install with pip install eth-account web3

# Generate key pair
def generate_keypair():
    acct = Account.create()
    return {
        "private_key": acct.key.hex(),
        "public_address": acct.address
    }

# Sings message
def sign_message(private_key: str, message: str) -> str:
    acct = Account.from_key(private_key)
    signed = acct.sign_message(eth_utils.messages.encode_defunct(text=message))
    return signed.signature.hex()

# Validate Signature
def verify_signature(message: str, signature: str, expected_address: str) -> bool:
    msg = eth_utils.messages.encode_defunct(text=message)
    signer = Account.recover_message(msg, signature=signature)
    return signer.lower() == expected_address.lower()

if __name__ == "__main__":
    # Demo
    kp = generate_keypair()
    print("Generated keypair:", kp)

    msg = "Vote for proposal A"
    sig = sign_message(kp["private_key"], msg)
    print("Signature:", sig)

    ok = verify_signature(msg, sig, kp["public_address"])
    print("Verified?", ok)
