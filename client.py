"""
    Test QUIC Client program.
"""

from QUIC import StreamFrame


def check_nth_bit_set(n, byte):
    i = 8-n
    if byte & (1 << i):
        return True
    else:
        return False

if __name__ == "__main__":
    # sock = QUICSocket()
    # sock.bind(("10.65.104.245", 8000))
    # sock.connect(("10.65.104.245", 8001))
    # msg = b"Hello from client."
    # print(f"Sending: {msg}")
    # sock.send(msg)
    # print(f"Received: {sock.recv(1024)}")
    # sock.close()
    # byte = 0xCC
    # for i in range(1, 9):
    #     print(check_nth_bit_set(i, byte))
    frame = StreamFrame(stream_id=b"1523", offset=b"10", length=b"100",data=b"awesome cool awesome ahahaha")
    print(frame.raw())