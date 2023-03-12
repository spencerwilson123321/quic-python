from QUIC import QUICSocket
from argparse import ArgumentParser

PARSER = ArgumentParser()
PARSER.add_argument("local_ip", help="The IPv4 address of this machine.")
PARSER.add_argument("server_ip", help="The IPv4 address of the server.")
PARSER.add_argument("server_port", help="The port number of the server.")

ARGS = PARSER.parse_args()

"""
    Test Case #1:
        1. Connect to the server.
        2. Attempt to send data on stream 1. 
        3. Check whether the bytes_sent is -1, this indicates that the peer closed the connection.
        4. Close the connection.
"""

if __name__ == "__main__":

    local_ip = ARGS.local_ip
    server_ip = ARGS.server_ip
    server_port = int(ARGS.server_port)

    client = QUICSocket(local_ip=local_ip)
    client.connect(address=(server_ip, server_port))
    msg = b"Hello"
    
    client.send(1, msg)
    print(f"Sent: {msg}")

    response = b""
    while not response:
        response, disconnected = client.recv(1, 1024)
    print(f"Received: {response}")

    client.send(1, msg)
    print(f"Sent: {msg}")

    response = b""
    while not response:
        response, disconnected = client.recv(1, 1024)
    print(f"Received: {response}")


    client.close()
