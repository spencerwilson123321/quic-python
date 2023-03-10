from QUIC import *

"""
    Test Case #1:
        1. Accept a client connection.
        2. Close the client connection.
"""

if __name__ == "__main__":

    server = QUICSocket(local_ip="10.0.0.131")
    server.listen(8000)
    client = server.accept() # Accept a connection.
    data = b""
    print("Receiving data...")
    while len(data) < 100:
        bytes_read, status = client.recv(1, 10)
        data += bytes_read
    print("Received all data.")
    client.send(1, b"all done")
