from QUIC import QUICSocket


if __name__ == "__main__":
    addr = ("10.0.0.159", 8001)
    sock = QUICSocket()
    sock.connect(addr)
    data, addr = sock.recv(1024)
    print(data)
    print(addr)
    sock.send(b"response")
    sock.close()
