from QUIC import QUICSocket

"""
    Test Case #3:
        1. Connect to the server.
        2. Transfer a somewhat large amount of data to the server.
        3. Close the connection.
"""

if __name__ == "__main__":
    client = QUICSocket(local_ip="10.0.0.159")
    client.connect(address=("10.0.0.131", 8000))
    data = b""
    with open("data.txt", "rb") as f:
        data = f.read()
    connection_open = True
    while connection_open:
        connection_open = client.send(1, data)
    print("server closed the connection")
    client.release()

