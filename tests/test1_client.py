from ..QUIC import QUICSocket

"""
    Test Case #1:
        1. Connect to the server.
        2. Attempt to read data from stream 1 (or attempt to send data on stream 1)
        3. Check whether the data is empty (this indicates that the connection is closed)
        4. Close the connection.
"""

if __name__ == "__main__":
    client = QUICSocket(local_ip="10.0.0.159")
    client.connect(address=("10.0.0.131", 8000))
    data = client.recv(1, 1024) # A return value of "" indicates that the connection has been closed by the peer.
    if not data:
        client.release() # This closes the socket but doesn't send a ConnectionClose frame.
