from QUIC import QUICSocket
from argparse import ArgumentParser

PARSER = ArgumentParser()
PARSER.add_argument("ip", help="The IPv4 address of this machine.")
PARSER.add_argument("port", help="The port number.")

ARGS = PARSER.parse_args()


"""
    Test Case #3:
        1. Accept client connection.
        2. Receive a somewhat large amount of data from the client.
        3. Close the connection.
"""

if __name__ == "__main__":
    ip = ARGS.ip
    port = int(ARGS.port)

    server = QUICSocket(local_ip=ip)
    server.listen(port)
    client = server.accept() # Accept a connection.
    disconnected = False
    data = b""
    # while not disconnected:
    while len(data) < 10000:
        received, disconnected = client.recv(1, 1024)
        data += received
    print(f"Received data: {data}")
    print("Client closed the connection.")
    client.release()           # Close the connection i.e. send ConnectionClose frame.
