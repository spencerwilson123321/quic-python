# quic-python

A QUIC Sockets implementation in Python that is designed to be similar to the built in `sockets` module in Python.

## Source Code Overview

### QUICSocket.py
The QUIC Sockets API

### QUICPacket.py
Defines all packet, header, and frame classes.

### QUICPacketBuilder.py
Abstraction layer for packet creation - performs input validation and error checking.

### QUICEncryption.py
Defines encryption context class which contains all data relevant to encryption.

### QUICConnection.py
Defines connection context class which contains the connection state/data.
