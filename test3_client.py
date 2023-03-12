from QUIC import QUICSocket
from argparse import ArgumentParser

PARSER = ArgumentParser()
PARSER.add_argument("local_ip", help="The IPv4 address of this machine.")
PARSER.add_argument("server_ip", help="The IPv4 address of the server.")
PARSER.add_argument("server_port", help="The port number of the server.")

ARGS = PARSER.parse_args()


"""
    Test Case #3:
        1. Connect to the server.
        2. Transfer a somewhat large amount of data to the server.
        3. Close the connection.
"""

if __name__ == "__main__":

    local_ip = ARGS.local_ip
    server_ip = ARGS.server_ip
    server_port = int(ARGS.server_port)

    client = QUICSocket(local_ip=local_ip)
    client.connect(address=(server_ip, server_port))
    data = b""
    with open("data.txt", "rb") as f:
        data = f.read()[0:10000]
    client.send(1, data)
    print(f"Sent: {data}")
    print("Closing the connection...")
    client.close()
