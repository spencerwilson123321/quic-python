from QUIC import QUICSocket
from socket import socket, AF_INET, SOCK_STREAM
from time import perf_counter

"""
    Measure and compare the speed of a large data transfer
    using QUIC and using TCP.
"""

if __name__ == "__main__":


    print("--- Testing QUIC Socket ---")
    client = QUICSocket(local_ip="10.0.0.159")
    client.connect(address=("10.0.0.131", 8000))
    data = b""

    with open("data.txt", "rb") as f:
        data = f.read()[0:50000]
    
    quic_start = perf_counter()
    client.send(1, data)
    quic_end = perf_counter()

    client.close()


    print("--- Testing TCP Socket ---")
    tcp_client = socket(AF_INET, SOCK_STREAM)
    tcp_client.connect(("10.0.0.131", 8001))
    tcp_start = perf_counter()
    tcp_client.sendall(data)
    tcp_end = perf_counter()
    tcp_client.close()

    print("--- Results ---")
    print(f"QUIC: {quic_end-quic_start} seconds")
    print(f"TCP: {tcp_end-tcp_start} seconds")
