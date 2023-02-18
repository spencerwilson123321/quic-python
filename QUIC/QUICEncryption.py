"""
    This module will define all the code for handling
    and implementing encryption over the QUIC connection.
    It defines the EncryptionContext class.
"""
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms
from secrets import token_bytes

# Hard coded for simplicity.
nonce = b"[\x8bp\xcbY\x7fA\xed\x01\xba\xcb\x14\x96t\\`"

class EncryptionContext:

    def __init__(self, key=None):
        if key:
            self.key = key
        else:
            self.key = token_bytes(32)
        self.nonce = nonce
        self.algorithm = algorithms.ChaCha20(self.key, self.nonce)
        self.cipher = Cipher(self.algorithm, mode=None, backend=None)
        self.encryptor = self.cipher.encryptor()
        self.decryptor = self.cipher.decryptor()

    def encrypt(self, plaintext: bytes) -> bytes:
        """
            Encrypts the given plaintext bytes.
        """
        return self.encryptor.update(plaintext)

    def decrypt(self, ciphertext: bytes) -> bytes:
        """
            Decrypts the given ciphertext bytes.
        """
        return self.decryptor.update(ciphertext)

