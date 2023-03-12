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
    msg = b"1234567890"

    print("Sending data...")
    for i in range(0, 10):    
        client.send(1, msg)
        print(f"Sent: {msg}")
    print("Waiting for response...")
    data = b""
    while not data:
        data, status = client.recv(1, 1024)
    print("Done.")
    client.close()
