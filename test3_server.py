from QUIC import QUICSocket

"""
    Test Case #3:
        1. Accept client connection.
        2. Receive a somewhat large amount of data from the client.
        3. Close the connection.
"""

if __name__ == "__main__":
    server = QUICSocket(local_ip="10.0.0.131")
    server.listen(8000)
    client = server.accept() # Accept a connection.
    bytes_read = 0
    data = b""
    while bytes_read < 1024:
        received = client.recv(1, 80)
        print(received)
        data += received
        bytes_read += len(received)
    print(f"Received data: {received}")
    client.release()           # Close the connection i.e. send ConnectionClose frame.
