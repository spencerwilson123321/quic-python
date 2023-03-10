from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from time import perf_counter

"""
    Measure and compare the speed of a large data transfer
    using QUIC and using TCP.
"""

if __name__ == "__main__":


    data = b""
    with open("data.txt", "rb") as f:
        data = f.read()[0:100000]

    print("--- Testing TCP Socket ---")
    tcp_client = socket(AF_INET, SOCK_STREAM)
    tcp_client.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    tcp_client.connect(("10.0.0.131", 8005))
    tcp_start = perf_counter()
    tcp_client.sendall(data)
    tcp_end = perf_counter()
    tcp_client.close()

    print("--- Results ---")
    print(f"TCP: {tcp_end-tcp_start} seconds")
