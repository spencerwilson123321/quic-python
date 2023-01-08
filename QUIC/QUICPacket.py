"""
    QUIC Packet module. Contains all classes that
    are used to represent QUIC packets.
"""
import struct


# ------------------ CONSTANTS --------------------------
LONG_HEADER_FORM = 0x80
SHORT_HEADER_FORM = 0x00
QUIC_VERSION = 0x36
CONN_ID_LEN = 0x04
PKT_NUM_LEN = 0x04
MAX_CONN_ID = 4294967295
MAX_PKT_NUM = 4294967295

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
        return self.header.raw()
    
    def __repr__(self) -> str:
        return f"----- Header -----\n {self.header}\n"


# ------------------ QUIC FRAMES ------------------------
# The first byte of every frame is the frame type, which is
# then followed by other type-specific fields.


# ------------------ FRAME TYPES ------------------------
# Each type is a single byte packed in big endian byte order.
FT_PADDING = struct.pack("!B", 0x00)
FT_PING = struct.pack("!B", 0x01)
FT_ACK = struct.pack("!B", 0x02)
FT_RESETSTREAM = struct.pack("!B", 0x04)
FT_STOPSENDING = struct.pack("!B", 0x05)
FT_CRYPTO = struct.pack("!B", 0x06)
FT_STREAM = struct.pack("!B", 0x08)
FT_MAXDATA = struct.pack("!B", 0x10)
FT_MAXSTREAMDATA = struct.pack("!B", 0x11)
FT_MAXSTREAMS = struct.pack("!B", 0x12)
FT_DATABLOCKED = struct.pack("!B", 0x14)
FT_STREAMDATABLOCKED = struct.pack("!B", 0x15)
FT_STREAMSBLOCKED = struct.pack("!B", 0x16)
FT_CONNECTIONCLOSE = struct.pack("!B", 0x1c)
FT_HANDSHAKEDONE = struct.pack("!B", 0x1e)


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

class LongHeader:
    """
    Long Header class which represents the QUIC Long Header.
        Fields:
            Header Form:
                The first bit of first byte. Represented in hex as 0x80 or 0x00 for long header and short header respectively.
            
            Type:
                The next seven bits of first byte. Can be Initial, Handshake, Retry, or 0-RTT: 0x00, 0x01, 0x02, 0x03 respectively.

            Version:
                The next byte represents the verison ID. This is a fixed value which represents a non-standard version of QUIC.

            Destination Connection ID Length:
                The next byte represents the destination connection ID length. This is a fixed value in units of bytes.
                The destination connection ID length will always be 4. Therefore this value should always be set to 0x04.
            
            Destination Connection ID:
                The destination connection ID is contained in the next 4 bytes.

            Source Connection ID Length:
                The next byte represents the source connection ID length. This is a fixed value in units of bytes.
                The source connection ID length will always be 4. Therefore this value should always be set to 0x04.
            
            Source Connection ID:
                The source connection ID is contained in the next 4 bytes.

            Packet Number Length:
                The next byte represents the packet number length. This is a fixed value in units of bytes.
                The packet number length will always be 4. Therefore this value should always be set to 0x04.
            
            Packet Number:
                The packet number is contained in the next 4 bytes.
            
            Length:
                The length is a 2 byte long field at the end of the header.
                The length of the rest of the packet i.e. the payload length (frames) in BYTES.
    """


    def __init__(self,
                type="initial", 
                destination_connection_id=0, 
                source_connection_id=0,
                packet_number=0
                ):

        # TODO add more error checking.
    
        # If type_to_hex returns None, then type argument is invalid.
        type_check = self.type_to_hex(type)
        if type_check == None:
            print(f"Invalid long header type received: {type}")
            exit(1)
        
        if destination_connection_id > MAX_CONN_ID:
            print(f"Invalid destination connection id: {destination_connection_id}.")
            print(f"Connection IDs must be less than {MAX_CONN_ID}.")
            exit(1)

        if source_connection_id > MAX_CONN_ID:
            print(f"Invalid source connection id: {source_connection_id}.")
            print(f"Connection IDs must be less than {MAX_CONN_ID}.")
            exit(1)

        if packet_number > MAX_PKT_NUM:
            print(f"Invalid packet number: {packet_number}.")
            print(f"Packet numbers must be less than {MAX_PKT_NUM}.")
            exit(1)

        self.header_form = LONG_HEADER_FORM
        self.type = type
        self.version = QUIC_VERSION
        self.destination_connection_id_len = CONN_ID_LEN
        self.destination_connection_id = destination_connection_id
        self.source_connection_id_len = CONN_ID_LEN
        self.source_connection_id = source_connection_id
        self.packet_number_length = PKT_NUM_LEN
        self.packet_number = packet_number
        self.length = 0x0000 # 0x0000 to 0xFFFF
    

    def type_to_hex(self, type: str) -> int:
        if type == "initial":
            return 0x00
        if type == "handshake":
            return 0x02
        if type == "retry":
            return 0x03
        return None
    

    def hex_to_type(self, value: str) -> int:
        if value == 0x00:
            return "initial"
        if value == 0x02:
            return "handshake"
        if value == 0x03:
            return "retry"
        return None
    

    def raw(self) -> bytes:
        """
            Returns the header as raw bytes in network byte order.
        """
        first_byte = self.header_form | self.type_to_hex(self.type)
        raw_bytes = struct.pack("!BBBLBLBLI", first_byte, self.version, self.destination_connection_id_len, self.destination_connection_id, self.source_connection_id_len, self.source_connection_id, self.packet_number_length, self.packet_number, self.length)
        return raw_bytes
    
    
    def __repr__(self) -> str:
        representation = "------ HEADER ------\n"
        representation += "Header Form: Long Header\n"
        representation += f"Type: {self.type} ({self.hex_to_type(self.type)})\n"
        representation += f"Version: {self.version}\n"
        representation += f"Destination Connection ID Length: {self.destination_connection_id_len}\n"
        representation += f"Destination Connection ID: {self.destination_connection_id}\n"
        representation += f"Source Connection ID Length: {self.source_connection_id_len}\n"
        representation += f"Source Connection ID: {self.source_connection_id}\n"
        representation += f"Packet Number Length: {self.packet_number_length}\n"
        representation += f"Packet Number: {self.packet_number}\n"
        representation += f"Payload Length: {self.length}\n"
        representation += "--------------------\n"
        return representation


class ShortHeader():
    
    def __init__(self, destination_connection_id, packet_number):
        self.type = None
        self.destination_connection_id = destination_connection_id       # 8 bytes
        self.packet_number = packet_number                               # 4 bytes
    
    def raw(self)  -> bytes:
        return self.type + self.destination_connection_id + self.packet_number

