"""
    Test QUIC Client program.
"""

from QUIC import QUICSocket

if __name__ == "__main__":
    sock = QUICSocket()
    sock.bind(("10.65.104.245", 8000))
    sock.connect(("10.65.104.245", 8001))
    msg = b"Hello from client."
    print(f"Sending: {msg}")
    sock.send(msg)
    print(f"Received: {sock.recv(1024)}")
    sock.close()
