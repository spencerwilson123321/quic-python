from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from argparse import ArgumentParser

PARSER = ArgumentParser()
PARSER.add_argument("server_ip", help="Server IPv4 address.")
PARSER.add_argument("server_port", help="Server port number")
PARSER.add_argument("n_bytes", help="Number of bytes to send.")

ARGS = PARSER.parse_args()


"""
    Test Case #3:
        1. Accept client connection.
        2. Receive a somewhat large amount of data from the client.
        3. Close the connection.
"""

if __name__ == "__main__":

    num = int(ARGS.n_bytes)
    ip = ARGS.server_ip
    port = int(ARGS.server_port)

    tcp_server = socket(AF_INET, SOCK_STREAM)
    tcp_server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    tcp_server.bind((ip, port))
    tcp_server.listen()
    print(f"Ready to read {num} bytes:")
    client, address = tcp_server.accept()
    data = b""
    while len(data) < num:
        data += client.recv(4096)
    client.close()
    tcp_server.close()
    print("TCP done.")
