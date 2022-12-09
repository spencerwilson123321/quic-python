"""
    Test QUIC server program.
"""

from QUIC import QUICSocket

if __name__ == "__main__":
    sock = QUICSocket(is_server=True)
    sock.bind(("", 8001))
    sock.listen(5)
    client, addr = sock.accept()
    data = client.recv(1024)
    client.send(data + b" Hello from server!")
    sock.close()
