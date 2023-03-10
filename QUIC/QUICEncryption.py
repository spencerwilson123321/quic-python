"""
    This module will define all the code for handling
    and implementing encryption over the QUIC connection.
    It defines the EncryptionContext class.
"""
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms
from cryptography.hazmat.primitives.ciphers.modes import CBC
from secrets import token_bytes

# Hard coded for simplicity.
temp = b'\xc0\x8bk ]I\x03\xecz\xb0vZ\xb7\xed*\xb9'

class EncryptionContext:

    def __init__(self, key=None):
        if key:
            self.key = key
        else:
            self.key = token_bytes(32)
        self.algorithm = algorithms.AES(self.key)
        self.cipher = Cipher(self.algorithm, mode=CBC(temp), backend=None)
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

