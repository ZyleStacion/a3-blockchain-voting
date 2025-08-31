from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def sign_vote(private_key_pem, vote_data):
    """
    Signs the vote data using the provided private key.
    """
    private_key = serialization.load_pem_private_key(
        private_key_pem,
        password=None,
    )
    signature = private_key.sign(
        vote_data.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature