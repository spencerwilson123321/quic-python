"""
    QUIC Packet module. Contains all classes that
    are used to represent QUIC packets.
"""

from enum import Enum
import struct


# ------------------ QUIC PACKET ------------------------
# All number fields are in Network-Byte Order (Big Endian)

class Packet():

    def __init__(self):
        self.type = None
        self.header = None
        self.frame = None


# ------------------ QUIC FRAMES ------------------------
# The first byte of every frame is the frame type, which is
# then followed by other type-specific fields.


# ------------------ FRAME TYPES ------------------------
# Each type is a single byte packed in big endian byte order.
PADDING = struct.pack(">B", 0x00)
PING = struct.pack(">B", 0x01)
ACK = struct.pack(">B", 0x02)
RESETSTREAM = struct.pack(">B", 0x04)
STOPSENDING = struct.pack(">B", 0x05)
CRYPTO = struct.pack(">B", 0x06)
STREAM = struct.pack(">B", 0x08)
MAXDATA = struct.pack(">B", 0x10)
MAXSTREAMDATA = struct.pack(">B", 0x11)
MAXSTREAMS = struct.pack(">B", 0x12)
DATABLOCKED = struct.pack(">B", 0x14)
STREAMDATABLOCKED = struct.pack(">B", 0x15)
STREAMSBLOCKED = struct.pack(">B", 0x16)
CONNECTIONCLOSE = struct.pack(">B", 0x1c)
HANDSHAKEDONE = struct.pack(">B", 0x1e)


class AckFrame:

    def __init__(self,
                largest_acknowledged = b"",
                ack_delay = b"",
                ack_range_count = b"",
                first_ack_range = b"",
                ack_range = b""):
        self.type = ACK
        self.largest_acknowledged = largest_acknowledged
        self.ack_delay = ack_delay
        self.ack_range_count = ack_range_count
        self.first_ack_range = first_ack_range
        self.ack_range = ack_range
    
    def raw(self) -> bytes:
        return b""

class CryptoFrame:
    
    def __init__(self):
        self.type = CRYPTO
        self.offset = b""
        self.length = b""
        self.data = b""
    
    def raw(self) -> bytes:
        return self.type + self.offset + self.length + self.data

class StreamFrame:

    def __init__(self, 
                stream_id: bytes = b"",
                offset: bytes = b"",
                length: bytes = b"",
                data: bytes = b""):
        self.type = STREAM
        self.stream_id = stream_id
        self.offset = offset
        self.length = length
        self.data = data

    def raw(self):
        return self.type + self.stream_id + self.offset + self.length + self.data

class PaddingFrame:

    def __init__(self):
        self.type = PADDING
    
    def raw(self):
        return self.type

class ResetStreamFrame:

    def __init__(self):
        self.type = RESETSTREAM

    def raw(self):
        return self.type

class StopSendingFrame:
    
    def __init__(self):
        self.type = STOPSENDING
    
    def raw(self):
        return self.type

class MaxDataFrame:
    
    def __init__(self):
        self.type = MAXDATA
    
    def raw(self):
        return self.type

class MaxStreamDataFrame:
    
    def __init__(self):
        self.type = MAXSTREAMDATA
    
    def raw(self):
        return self.type

class MaxStreamsFrame:
    
    def __init__(self):
        self.type = MAXSTREAMS
    
    def raw(self):
        return self.type

class DataBlockedFrame:
    
    def __init__(self):
        self.type = DATABLOCKED
    
    def raw(self):
        return self.type

class StreamDataBlockedFrame:
    
    def __init__(self):
        self.type = STREAMDATABLOCKED
    
    def raw(self):
        return self.type

class StreamsBlockedFrame:
    
    def __init__(self):
        self.type = STREAMSBLOCKED
    
    def raw(self):
        return self.type

class ConnectionCloseFrame:
    
    def __init__(self):
        self.type = CONNECTIONCLOSE
    
    def raw(self):
        return self.type

class HandshakeDoneFrame:
    
    def __init__(self):
        self.type = HANDSHAKEDONE

    def raw(self):
        return self.type

# ----------------------- QUIC HEADERS ------------------------------
# QUIC Packets have two header formats: Long Header and Short Header.
# The type is set in the first octet of the QUIC header.

# ----------------- QUIC Long Header Format -----------------------
#  0                   1                   2                   3
#  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
# +-+-+-+-+-+-+-+-+
# |1|   Type (7)  |
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# |                                                               |
# +                       Connection ID (64)                      +
# |                                                               |
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# |                       Packet Number (32)                      |
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# |                         Version (32)                          |
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# |                          Payload (*)                        ...
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

class LongHeader():
    
    def __init__(self):
        self.header_form = None                     # first bit of first byte
        self.type = None                            # remaining 7 bits of first byte
        self.version = None                         # 4 bytes
        self.destination_connection_id_len = None   # 1 byte
        self.destination_connection_id = None       # 0...20 bytes
        self.source_connection_id_len = None        # 1 bytes
        self.source_connection_id = None            # 0...20 bytes
        self.packet_number_len = None               # 1 byte
        self.packet_number = None                   # 1 to 4 bytes long
        self.length = None                          # variable length integer.


# ----------------- Short Header Format ---------------------------
#  0                   1                   2                   3
#  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
# +-+-+-+-+-+-+-+-+
# |0|C|K| Type (5)|
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# |                                                               |
# +                     [Connection ID (64)]                      +
# |                                                               |
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# |                      Packet Number (8/16/32)                ...
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# |                     Protected Payload (*)                   ...
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

class ShortHeader():
    
    def __init__(self):
        self.header_form = None         # first bit of first byte
        self.connection_id_flag = None  # second bit of first byte
        self.key_phase_bit = None       # third bit of first byte
        self.type = None                # remaining 5 bits of first byte
        self.connection_id = None       # 8 bytes
        self.packet_number = None       # 1, 2, or 4 bytes long depending on the header type
