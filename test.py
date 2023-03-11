
import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

key = os.urandom(32)

iv = os.urandom(16)

cipher = Cipher(algorithms.AES(key), modes.CBC(iv))

encryptor = cipher.encryptor()

ct = encryptor.update(b"a secret message") + encryptor.finalize()

decryptor = cipher.decryptor()

decrypted = decryptor.update(ct) + decryptor.finalize()

print(decrypted)