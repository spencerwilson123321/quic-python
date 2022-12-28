# quic-python
A QUIC implementation in Python

## Project Structure

QUIC/                       contains all source code files for QUIC sockets api
QUIC/QUICSocket.py          The QUIC Sockets API
QUIC/QUICPacket.py          Defines all packet, header, and frame classes.
QUIC/QUICPacketBuilder.py   Abstraction layer for packet creation - performs input validation and error checking.
QUIC/QUICEncryption.py      Defines encryption context class which contains all data relevant to encryption.
QUIC/QUICConnection.py      Defines connection context class which contains the connection state/data.
    