# quic-python

A sockets-like QUIC implementation in Python that is designed to be similar to the built in `sockets` module in Python. This is my capstone project for my Bachelors in Technology at BCIT.

## Project Overview

### QUICSocket.py
This module contains the QUICSocket class which is the general abstraction over the QUIC implementation which can be used to implement general networking applications.

### QUICPacket.py
This module contains all of the packet, header, and frame definitions. It allows one to construct QUIC packets of various types. Each component implements the serializable interface which allows each component to be serialized (turned into network packed bytes) easily.

### QUICEncryption.py
Defines encryption context class which contains all data relevant to encryption. It allows packet bytes to be encrypted on the wire.

### QUICConnection.py
This module defines the ConnectionContext class which holds all of the relevant connection state for a QUIC connection.

## Examples

```python
client = QUICSocket(local_ip="10.0.0.159")
client.connect(("10.0.0.131", 8000))
client.send(1, b"Hello world!")
client.close()
```

```python
server = QUICSocket(local_ip="10.0.0.131")
server.bind(8000)
server.listen()
client = server.accept()
disconnected = False
while not disconnected:
    data, status = client.recv(1, 1024)
    if data:
        print(f"Received: {data}")
client.release()
```
