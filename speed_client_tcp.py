from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from time import perf_counter
from argparse import ArgumentParser

PARSER = ArgumentParser()
PARSER.add_argument("server_ip", help="Server IPv4 address.")
PARSER.add_argument("server_port", help="Server port number")
PARSER.add_argument("n_bytes", help="Number of bytes to send.")

ARGS = PARSER.parse_args()


"""
    Measure and compare the speed of a large data transfer
    using QUIC and using TCP.
"""

if __name__ == "__main__":

    server_ip = ARGS.server_ip
    server_port = int(ARGS.server_port)
    num = int(ARGS.n_bytes)

    data = b""
    with open("data.txt", "rb") as f:
        data = f.read()[0:num]

    print("--- Testing TCP Socket ---")
    tcp_client = socket(AF_INET, SOCK_STREAM)
    tcp_client.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    tcp_client.connect((server_ip, server_port))
    tcp_start = perf_counter()
    tcp_client.sendall(data)
    tcp_end = perf_counter()
    tcp_client.close()

    print("--- Results ---")
    print(f"TCP: {tcp_end-tcp_start} seconds")
