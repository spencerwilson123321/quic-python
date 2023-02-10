from ..QUIC import QUICSocket

"""
    Test Case #1:
        1. Connect to the server.
        2. Attempt to send data on stream 1. 
        3. Check whether the bytes_sent is -1, this indicates that the peer closed the connection.
        4. Close the connection.
"""

if __name__ == "__main__":
    client = QUICSocket(local_ip="10.0.0.159")
    client.connect(address=("10.0.0.131", 8000))
    bytes_sent = client.send(1, b"Hello world!")
    if bytes_sent == -1:
        client.release()
