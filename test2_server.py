from QUIC import QUICSocket
from argparse import ArgumentParser

PARSER = ArgumentParser()
PARSER.add_argument("ip", help="The IPv4 address of this machine.")
PARSER.add_argument("port", help="The port number.")

ARGS = PARSER.parse_args()


"""
    Test Case #1:
        1. Accept a client connection.
        2. Close the client connection.
"""

if __name__ == "__main__":
    ip = ARGS.ip
    port = int(ARGS.port)

    server = QUICSocket(local_ip=ip)
    server.listen(port)
    client = server.accept() # Accept a connection.
    
    msg = b""
    while not msg:
        msg, disconnected = client.recv(1, 1024)
    print(f"Received: {msg}")

    client.send(1, msg)
    print(f"Sent: {msg}")

    msg = b""
    while not msg:
        msg, disconnected = client.recv(1, 1024)
    print(f"Received: {msg}")

    client.send(1, msg)
    print(f"Sent: {msg}")


    client.release()
