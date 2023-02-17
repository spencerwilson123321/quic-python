from QUIC import EncryptionContext

ec = EncryptionContext()

msg = b"Testing Encryption!"

print(f"Before Encryption: {msg}")
print(f"Size: {len(msg)}")

msg = ec.encrypt(msg)

print(f"After Encryption: {msg}")
print(f"Size: {len(msg)}")

msg = ec.decrypt(msg)

print(f"After Decryption: {msg}")
print(f"Size: {len(msg)}")
