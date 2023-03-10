from QUIC import QUICSocket
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from time import perf_counter

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
    while len(data) < 50000:
        received, disconnected = client.recv(1, 1024)
        data += received
    client.release()           # Close the connection i.e. send ConnectionClose frame.
    print("QUIC done.")


    tcp_server = socket(AF_INET, SOCK_STREAM)
    tcp_server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    tcp_server.bind(("10.0.0.131", 8001))
    tcp_server.listen(5)
    client = tcp_server.accept()
    data = b""
    while len(data) < 800000:
        data += client.recv(4096)
    client.close()
    tcp_server.close()
    print("TCP done.")