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
    disconnected = False
    data = b""
    # while not disconnected:
    while len(data) < 1024:
        received, disconnected = client.recv(1, 120)
        data += received
    print(f"Received data: {data}")
    print("Client closed the connection.")
    client.release()           # Close the connection i.e. send ConnectionClose frame.
