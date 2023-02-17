"""
    This module will define all the code for handling
    and implementing encryption over the QUIC connection.
    It defines the EncryptionContext class.
"""
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms
from os import urandom
from secrets import token_bytes

class EncryptionContext:

    def __init__(self):
        self.key = token_bytes(32)
        self.nonce = urandom(16)
        self.algorithm = algorithms.ChaCha20(self.key, self.nonce)
        self.cipher = Cipher(self.algorithm, mode=None, backend=None)
        self.encryptor = self.cipher.encryptor()
        self.decryptor = self.cipher.decryptor()

    def encrypt(self, plaintext: bytes) -> bytes:
        return self.encryptor.update(plaintext)

    def decrypt(self, ciphertext: bytes) -> bytes:
        return self.decryptor.update(ciphertext)

