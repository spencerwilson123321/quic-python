from QUIC import QUICSocket
from argparse import ArgumentParser

PARSER = ArgumentParser()
PARSER.add_argument("ip", help="IPv4 address")
PARSER.add_argument("port", help="Port number")
PARSER.add_argument("n_bytes", help="Number of bytes to receive.")

ARGS = PARSER.parse_args()


"""
    Test Case #3:
        1. Accept client connection.
        2. Receive a somewhat large amount of data from the client.
        3. Close the connection.
"""

if __name__ == "__main__":
    server = QUICSocket(local_ip="10.0.0.131")
    server.listen(8000)
    ip = ARGS.ip
    port = ARGS.port
    num = int(ARGS.n_bytes)
    print(f"Ready to read {num} bytes:")
    client = server.accept()
    disconnected = False
    data = b""

    while len(data) < num:
        received, disconnected = client.recv(1, 1024)
        data += received
    client.release()
    print("Done.")
