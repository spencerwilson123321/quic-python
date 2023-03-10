from QUIC import QUICSocket
from sys import argv

"""
    Test Case #3:
        1. Accept client connection.
        2. Receive a somewhat large amount of data from the client.
        3. Close the connection.
"""

if __name__ == "__main__":
    server = QUICSocket(local_ip="10.0.0.131")
    server.listen(8000)
    num = int(argv[1])
    client = server.accept()
    disconnected = False
    data = b""

    print(f"Ready to read {num} bytes:")
    while len(data) < num:
        received, disconnected = client.recv(1, 1024)
        data += received
    client.release()
    print("Done.")
