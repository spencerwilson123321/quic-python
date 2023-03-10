from QUIC import QUICSocket
from time import perf_counter
from argparse import ArgumentParser

PARSER = ArgumentParser()
PARSER.add_argument("local ip", help="Local IPv4 address.")
PARSER.add_argument("server ip", help="Server IPv4 address.")
PARSER.add_argument("server port", help="Server port number")
PARSER.add_argument("n_bytes", help="Number of bytes to send.")

ARGS = PARSER.parse_args()


"""
    Measure and compare the speed of a large data transfer
    using QUIC and using TCP.
"""

if __name__ == "__main__":

    local_ip = ARGS.local_ip
    server_ip = ARGS.server_ip
    server_port = int(ARGS.server_port)
    num = int(ARGS.n_bytes)

    print("--- Testing QUIC Socket ---")
    client = QUICSocket(local_ip=local_ip)
    client.connect(address=(server_ip, server_port))
    data = b""

    with open("data.txt", "rb") as f:
        data = f.read()[0:num]
    
    quic_start = perf_counter()
    client.send(1, data)
    quic_end = perf_counter()
    client.close()

    print("--- Results ---")
    print(f"QUIC: {quic_end-quic_start} seconds")
