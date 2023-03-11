"""
    This module will define all the code for handling
    and implementing encryption over the QUIC connection.
    It defines the EncryptionContext class.
"""
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os


class EncryptionContext:

    def __init__(self, key=None):
        if key:
            self.key = key
        else:
            self.key = os.urandom(32)
        self.iv = os.urandom(16)
        self.cipher = Cipher(algorithms.AES(self.key), modes.CBC(self.iv))

    def encrypt(self, data):
        while len(data) % 16 != 0:
            data += b" "
        encryptor = self.cipher.encryptor()
        return encryptor.update(data) + encryptor.finalize()

    def decrypt(self, data):
        decryptor = self.cipher.decryptor()
        plain = decryptor.update(data) + decryptor.finalize()
        plain = plain.strip()
        return plain
