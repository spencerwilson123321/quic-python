from QUIC import QUICSocket

if __name__ == "__main__":
    server_addr = ("", 8001)
    sock = QUICSocket()
    sock.bind(server_addr)
    # sock.listen(1)         
    client = sock.accept()
    client.send(b"data", 1)
    print("Sent: b'data'")
    data, addr = client.recv(1024)
    print(f"Received: {data} - From: {addr}")
    client.close()
