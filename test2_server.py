from QUIC import QUICSocket

"""
    Test Case #1:
        1. Accept a client connection.
        2. Close the client connection.
"""

if __name__ == "__main__":
    server = QUICSocket(local_ip="10.0.0.131")
    client = server.accept() # Accept a connection.
    client.close()           # Close the connection i.e. send ConnectionClose frame.
