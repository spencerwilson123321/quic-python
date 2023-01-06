"""
    QUIC Packet module. Contains all classes that
    are used to represent QUIC packets.
"""
import struct


# ------------------ QUIC PACKET ------------------------
# All number fields are in Network-Byte Order (Big Endian)

class Packet():
    """
        This represents any QUIC packet. A QUIC packet contains
        a header and one or more frames.
    """

    def __init__(self, header=None, frames=[]):
        self.header = header
        self.frames = frames
    
    def raw(self) -> bytes:
        return b""
    
    def __repr__(self) -> str:
        return f"----- Header -----\n {self.header}\n"


# ------------------ QUIC FRAMES ------------------------
# The first byte of every frame is the frame type, which is
# then followed by other type-specific fields.


# ------------------ FRAME TYPES ------------------------
# Each type is a single byte packed in big endian byte order.
FT_PADDING = struct.pack(">B", 0x00)
FT_PING = struct.pack(">B", 0x01)
FT_ACK = struct.pack(">B", 0x02)
FT_RESETSTREAM = struct.pack(">B", 0x04)
FT_STOPSENDING = struct.pack(">B", 0x05)
FT_CRYPTO = struct.pack(">B", 0x06)
FT_STREAM = struct.pack(">B", 0x08)
FT_MAXDATA = struct.pack(">B", 0x10)
FT_MAXSTREAMDATA = struct.pack(">B", 0x11)
FT_MAXSTREAMS = struct.pack(">B", 0x12)
FT_DATABLOCKED = struct.pack(">B", 0x14)
FT_STREAMDATABLOCKED = struct.pack(">B", 0x15)
FT_STREAMSBLOCKED = struct.pack(">B", 0x16)
FT_CONNECTIONCLOSE = struct.pack(">B", 0x1c)
FT_HANDSHAKEDONE = struct.pack(">B", 0x1e)


class AckFrame:

    def __init__(self,
                largest_acknowledged = None,
                ack_delay = None,
                ack_range_count = None,
                first_ack_range = None,
                ack_range = None):
        self.type = FT_ACK
        self.largest_acknowledged = largest_acknowledged
        self.ack_delay = ack_delay
        self.ack_range_count = ack_range_count
        self.first_ack_range = first_ack_range
        self.ack_range = ack_range
    
    def raw(self) -> bytes:
        return b""

class CryptoFrame:
    
    def __init__(self, offset=None, length=None, data=None):
        self.type = FT_CRYPTO
        self.offset = offset
        self.length = length
        self.data = data
    
    def raw(self) -> bytes:
        return self.type + self.offset + self.length + self.data

class StreamFrame:

    def __init__(self, 
                stream_id = None,
                offset = None,
                length = None,
                data = None):
        self.type = FT_STREAM
        self.stream_id = stream_id
        self.offset = offset
        self.length = length
        self.data = data

    def raw(self):
        return self.type + self.stream_id + self.offset + self.length + self.data

class PaddingFrame:

    def __init__(self):
        self.type = FT_PADDING
    
    def raw(self):
        return self.type

class ResetStreamFrame:

    def __init__(self, stream_id=b"", error_code=b"", final_size=b""):
        self.type = FT_RESETSTREAM
        self.stream_id = stream_id
        self.error_code = error_code
        self.final_size = final_size

    def raw(self):
        return self.type + self.stream_id + self.error_code + self.final_size

class StopSendingFrame:
    
    def __init__(self, stream_id=b"", error_code=b""):
        self.type = FT_STOPSENDING
        self.stream_id = stream_id
        self.error_code = error_code
    
    def raw(self):
        return self.type + self.stream_id + self.error_code

class MaxDataFrame:
    
    def __init__(self, max_data=b""):
        self.type = FT_MAXDATA
        self.max_data = max_data
    
    def raw(self):
        return self.type + self.max_data

class MaxStreamDataFrame:
    
    def __init__(self, stream_id=b"", max_stream_data=b""):
        self.type = FT_MAXSTREAMDATA
        self.stream_id = stream_id
        self.max_stream_data = max_stream_data
    
    def raw(self):
        return self.type + self.stream_id + self.max_stream_data

class MaxStreamsFrame:
    
    def __init__(self, max_streams=b""):
        self.type = FT_MAXSTREAMS
        self.max_streams = max_streams
    
    def raw(self):
        return self.type + self.max_streams

class DataBlockedFrame:
    
    def __init__(self, max_data=b""):
        self.type = FT_DATABLOCKED
        self.max_data = max_data
    
    def raw(self):
        return self.type + self.max_data

class StreamDataBlockedFrame:
    
    def __init__(self, stream_id=b"", max_stream_data=b""):
        self.type = FT_STREAMDATABLOCKED
        self.stream_id = stream_id
        self.max_stream_data = max_stream_data
    
    def raw(self):
        return self.type + self.stream_id + self.max_stream_data

class StreamsBlockedFrame:
    
    def __init__(self, max_streams=b""):
        self.type = FT_STREAMSBLOCKED
        self.max_streams = max_streams
    
    def raw(self):
        return self.type + self.max_streams

class ConnectionCloseFrame:
    
    def __init__(self, error_code=b"", reason_phrase_len=b"", reason_phrase=b""):
        self.type = FT_CONNECTIONCLOSE
        self.error_code = error_code
        self.reason_phrase_len = reason_phrase_len
        self.reason_phrase = reason_phrase
    
    def raw(self):
        return self.type + self.error_code + self.reason_phrase_len + self.reason_phrase

class HandshakeDoneFrame:
    
    def __init__(self):
        self.type = FT_HANDSHAKEDONE

    def raw(self):
        return self.type

# ----------------------- QUIC HEADERS ------------------------------
# QUIC Packets have two header formats: Long Header and Short Header.
# The type is set in the first octet of the QUIC header.

# ----------------- QUIC Long Header Format -----------------------
#  0                   1                   2                   3
#  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
# +-+-+-+-+-+-+-+-+
# |f(1)| Type (7) |
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

class LongHeader:
    """
        LongHeader class which can be one of many types. The different types don't affect
        the header fields structure, only the way they are interpreted. So to me it does not
        make sense to make classes for each header type.
    """

    def __init__(self, type):
        self.header_form = None # first bit of first byte which represents whether the packet is long or short header format.
        self.type = type # The last 7 bits of the first byte of all headers is the type.
        self.version = None # 4 bytes and hardcoded.
        self.destination_connection_id_len = None   # 1 byte
        self.destination_connection_id = None       # 0...20 bytes
        self.source_connection_id_len = None        # 1 bytes
        self.source_connection_id = None            # 0...20 bytes
        self.packet_number_length = None               # 1 byte
        self.packet_number = None                   # 1 to 4 bytes long
        self.length = None                          # variable length integer.
    
    def raw(self) -> bytes:
        return b""

# ----------------- Short Header Format ---------------------------
#  0                   1                   2                   3
#  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
# +-+-+-+-+-+-+-+-+
# |    Type (8)   |
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
    
    def __init__(self, destination_connection_id, packet_number):
        self.type = None
        self.destination_connection_id = destination_connection_id       # 8 bytes
        self.packet_number = packet_number                               # 4 bytes
    
    def raw(self)  -> bytes:
        return self.type + self.destination_connection_id + self.packet_number

if __name__ == "__main__":
    pass
