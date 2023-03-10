from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from sys import argv

"""
    Test Case #3:
        1. Accept client connection.
        2. Receive a somewhat large amount of data from the client.
        3. Close the connection.
"""

if __name__ == "__main__":

    num = int(argv[1])
    tcp_server = socket(AF_INET, SOCK_STREAM)
    tcp_server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    tcp_server.bind(("10.0.0.131", 8005))
    tcp_server.listen()
    print(f"Ready to read {num} bytes:")
    client, address = tcp_server.accept()
    data = b""
    while len(data) < num:
        data += client.recv(4096)
    client.close()
    tcp_server.close()
    print("TCP done.")
