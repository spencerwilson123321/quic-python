from QUIC import *
from argparse import ArgumentParser

PARSER = ArgumentParser()
PARSER.add_argument("local_ip", help="The IPv4 address of this machine.")
PARSER.add_argument("port", help="The port number.")
ARGS = PARSER.parse_args()

"""
    Test Case #1:
        1. Accept a client connection.
        2. Close the client connection.
"""

if __name__ == "__main__":
    local_ip = ARGS.local_ip
    port = int(ARGS.port)
    server = QUICSocket(local_ip=local_ip)
    server.listen(port)
    client = server.accept() # Accept a connection.
    data = b""
    print("Receiving data...")
    while len(data) < 100:
        bytes_read, status = client.recv(1, 10)
        data += bytes_read
        if bytes_read:
            print(bytes_read)
    print("Received all data.")
    client.send(1, b"all done")
