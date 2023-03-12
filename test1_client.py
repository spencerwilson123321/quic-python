from QUIC import QUICSocket
from argparse import ArgumentParser

PARSER = ArgumentParser()
PARSER.add_argument("local_ip")
PARSER.add_argument("server_ip")
PARSER.add_argument("server_port")

ARGS = PARSER.parse_args()

"""
    Test Case #1:
        1. Connect to the server.
        2. Attempt to read data from stream 1 (or attempt to send data 
        on stream 1)
        3. Check whether the data is empty (this indicates that the 
        connection is closed)
        4. Close the connection.
"""

if __name__ == "__main__":

    local_ip = ARGS.local_ip
    server_ip = ARGS.server_ip
    server_port = int(ARGS.server_port)

    client = QUICSocket(local_ip=local_ip)
    client.connect(address=(server_ip, server_port))
    status = client.send(1, b"Very cool.")
    client.close()
