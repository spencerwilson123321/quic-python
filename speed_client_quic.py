from QUIC import QUICSocket
from time import perf_counter
from sys import argv

"""
    Measure and compare the speed of a large data transfer
    using QUIC and using TCP.
"""

if __name__ == "__main__":


    print("--- Testing QUIC Socket ---")
    client = QUICSocket(local_ip="10.0.0.159")
    client.connect(address=("10.0.0.131", 8000))
    data = b""
    num = int(argv[1])
    with open("data.txt", "rb") as f:
        data = f.read()[0:num]
    
    quic_start = perf_counter()
    client.send(1, data)
    quic_end = perf_counter()
    client.close()

    print("--- Results ---")
    print(f"QUIC: {quic_end-quic_start} seconds")
