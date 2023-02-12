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
    data = b""
    while True:
        received = client.recv(1, 1024)
        if not received:
            break
        data += received
    print(f"Received data: {data}")
    print(f"Client Closed Connection:\n {data}")
    client.release()           # Close the connection i.e. send ConnectionClose frame.
