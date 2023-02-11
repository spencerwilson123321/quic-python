from QUIC import QUICSocket

"""
    Test Case #1:
        1. Accept a client connection.
        2. Close the client connection.
"""

if __name__ == "__main__":
    server = QUICSocket(local_ip="10.0.0.131")
    server.listen(8000)
    client = server.accept() # Accept a connection.
    msg = client.recv(1, 1024)
    print(f"Received: {msg}")
    client.close()
