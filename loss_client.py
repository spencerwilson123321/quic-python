from QUIC import QUICSocket
import time

"""
    Test Case #1:
        1. Connect to the server.
        2. Attempt to send data on stream 1. 
        3. Check whether the bytes_sent is -1, this indicates that the peer closed the connection.
        4. Close the connection.
"""

if __name__ == "__main__":
    client = QUICSocket(local_ip="10.0.0.159")
    client.connect(address=("10.0.0.131", 8000))
    msg = b"Hello"

    for i in range(0, 5):    
        client.send(1, msg)
        print(f"Sent: {msg}")
    
    data = b""
    while not data:
        client.recv(1, 1024)


    client.close()
