"""
    QUIC Packet module. Contains all classes that
    are used to represent QUIC packets.
"""
import struct


# ------------------ DATA --------------------------

# DATA SIZES:
MAX_LONG = 18446744073709551615   # 8 bytes max - Use Q in struct.pack
MAX_INT = 4294967295              # 4 bytes max - Use I in struct.pack
MAX_SHORT = 65535                 # 2 bytes max - Use H in struct.pack
MAX_CHAR = 255                    # 1 byte max  - Use B in struct.pack


# HEADER INFO:
HF_LONG = 0x80
HF_SHORT = 0x00

HT_INITIAL = 0x00
HT_HANDSHAKE = 0x02
HT_RETRY = 0x03
HT_DATA = 0x04

QUIC_VERSION = 0x36
CONN_ID_LEN = 0x04
PKT_NUM_LEN = 0x04


# FRAME TYPES:
FT_PADDING = 0x00
FT_PING = 0x01
FT_ACK = 0x02
FT_RESETSTREAM = 0x04
FT_STOPSENDING = 0x05
FT_CRYPTO = 0x06
FT_STREAM = 0x08
FT_MAXDATA = 0x10
FT_MAXSTREAMDATA = 0x11
FT_MAXSTREAMS = 0x12
FT_DATABLOCKED = 0x14
FT_STREAMDATABLOCKED = 0x15
FT_STREAMSBLOCKED = 0x16
FT_CONNECTIONCLOSE = 0x1c
FT_HANDSHAKEDONE = 0x1e


# STRING CONSTANTS
STR_INITIAL = "INITIAL"
STR_HANDSHAKE = "HANDSHAKE"
STR_RETRY = "RETRY"
STR_PADDING = "PADDING"
STR_PING = "PING"
STR_ACK = "ACK"
STR_RESETSTREAM = "RESETSTREAM"
STR_STOPSENDING = "STOPSENDING"
STR_CRYPTO = "CRYPTO"
STR_STREAM = "STREAM"
STR_MAXDATA = "MAXDATA"
STR_MAXSTREAMDATA = "MAXSTREAMDATA"
STR_MAXSTREAMS = "MAXSTREAMS"
STR_DATABLOCKED = "DATABBLOCKED"
STR_STREAMDATABLOCKED = "STREAMDATABLOCKED"
STR_STREAMSBLOCKED = "STREAMSBLOCKED"
STR_CONNECTIONCLOSE = "CONNECTIONCLOSE"
STR_HANDSHAKEDONE = "HANDSHAKEDONE"

# ------------------ EXCEPTIONS -----------------

class ShortValueError(Exception): pass
class LongValueError(Exception): pass
class IntValueError(Exception): pass
class CharValueError(Exception): pass


# ------------------ FUNCTIONS ------------------


def check_long_type(var_name: str, var: int) -> None:
    if var < 0:
        raise LongValueError(f"Variable '{var_name}' cannot be negative. '{var_name}' value: {var}")
    if var > MAX_LONG:
        raise LongValueError(f"Variable '{var_name}' cannot be greater than {MAX_LONG}. '{var_name}' value: {var}")
    return None


def check_int_type(var_name: str, var: int) -> None:
    if var < 0:
        raise IntValueError(f"Variable '{var_name}' cannot be negative. '{var_name}' value: {var}")
    if var > MAX_INT:
        raise IntValueError(f"Variable '{var_name}' cannot be greater than {MAX_INT}. '{var_name}' value: {var}")
    return None


def check_short_type(var_name: str, var: int) -> None:
    if var < 0:
        raise ShortValueError(f"Variable '{var_name}' cannot be negative. '{var_name}' value: {var}")
    if var > MAX_SHORT:
        raise ShortValueError(f"Variable '{var_name}' cannot be greater than {MAX_SHORT}. '{var_name}' value: {var}")
    return None


def check_char_type(var_name: str, var: int) -> None:
    if var < 0:
        raise CharValueError(f"Variable '{var_name}' cannot be negative. '{var_name}' value: {var}")
    if var > MAX_CHAR:
        raise ShortValueError(f"Variable '{var_name}' cannot be greater than {MAX_CHAR}. '{var_name}' value: {var}")
    return None


def header_type_string_to_hex(type: str) -> int:
    if type == STR_INITIAL:
        return HT_INITIAL
    if type == STR_HANDSHAKE:
        return HT_HANDSHAKE
    if type == STR_RETRY:
        return HT_RETRY
    return None


def header_type_hex_to_string(type: int) -> str:
    if type == HT_INITIAL:
        return STR_INITIAL
    if type == HT_HANDSHAKE:
        return STR_HANDSHAKE
    if type == HT_RETRY:
        return STR_RETRY
    return None


def frame_type_hex_to_string(type: int) -> str:
    if type == FT_PADDING:
        return STR_PADDING
    if type == FT_PING:
        return STR_PING
    if type == FT_ACK:
        return STR_ACK
    if type == FT_RESETSTREAM:
        return STR_RESETSTREAM
    if type == FT_STOPSENDING:
        return STR_STOPSENDING
    if type == FT_CRYPTO:
        return STR_CRYPTO
    if type == FT_STREAM:
        return STR_STREAM
    if type == FT_MAXDATA:
        return STR_MAXDATA
    if type == FT_MAXSTREAMDATA:
        return STR_MAXSTREAMDATA
    if type == FT_MAXSTREAMS:
        return STR_MAXSTREAMS
    if type == FT_DATABLOCKED:
        return STR_DATABLOCKED
    if type == FT_STREAMDATABLOCKED:
        return STR_STREAMDATABLOCKED
    if type == FT_STREAMSBLOCKED:
        return STR_STREAMSBLOCKED
    if type == FT_CONNECTIONCLOSE:
        return STR_CONNECTIONCLOSE
    if type == FT_HANDSHAKEDONE:
        return STR_HANDSHAKEDONE
    return None


def frame_type_string_to_hex(type: str) -> int:
    if type == STR_PADDING:
        return FT_PADDING
    if type == STR_PING:
        return FT_PING
    if type == STR_ACK:
        return FT_ACK
    if type == STR_RESETSTREAM:
        return FT_RESETSTREAM
    if type == STR_STOPSENDING:
        return FT_STOPSENDING
    if type == STR_CRYPTO:
        return FT_CRYPTO
    if type == STR_STREAM:
        return FT_STREAM
    if type == STR_MAXDATA:
        return FT_MAXDATA
    if type == STR_MAXSTREAMDATA:
        return FT_MAXSTREAMDATA
    if type == STR_MAXSTREAMS:
        return FT_MAXSTREAMS
    if type == STR_DATABLOCKED:
        return FT_DATABLOCKED
    if type == STR_STREAMDATABLOCKED:
        return FT_STREAMDATABLOCKED
    if type == STR_STREAMSBLOCKED:
        return FT_STREAMSBLOCKED
    if type == STR_CONNECTIONCLOSE:
        return FT_CONNECTIONCLOSE
    if type == STR_HANDSHAKEDONE:
        return FT_HANDSHAKEDONE
    return None


# ------------------ CLASSES ------------------

class Packet():
    """
        This represents any QUIC packet. A QUIC packet contains
        a header and one or more frames.
    """

    def __init__(self, header=None, frames=[]):
        self.header = header
        self.frames = frames

    def raw(self) -> bytes:
        frame_data = b""
        for frame in self.frames:
            frame_data += frame.raw()
        return self.header.raw() + frame_data

    def __repr__(self) -> str:
        representation = ""
        representation += f"{self.header}\n"
        for frame in self.frames:
            representation += frame.__repr__() + "\n"
        return representation


class AckRange:
    """
        An ACK Range contains two fields:
            Gap:
                The first 4 bytes of the ACK range is the Gap value.
            Ack Range Length:
                The next 4 bytes is the Ack Range Length. 
    """

    def __init__(self, gap: int, ack_range_length: int):

        check_int_type("gap", gap)
        check_int_type("ack_range_length", ack_range_length)

        self.gap = gap
        self.ack_range_length = ack_range_length
    
    def raw(self) -> bytes:
        return struct.pack("!II", self.gap, self.ack_range_length)


class AckFrame:
    """
        ACK Frame Format:
            Type:
                The first byte of the frame is the type.
            Largest Acknowledged:
                The next 4 bytes is the Largest Acknowledged field.
                The Largest Ackowledged field is the largest packet number being acknowledged i.e. the largest packet number seen so far.
                In other words, the largest packet number that the peer has received prior to creating the Ack Frame.
            ACK Delay:
                The next 4 bytes is the acknowledgement delay in microseconds.
            ACK Range Count:
                The next 4 bytes is the ACK range count.
                The ACK range count is the number of ack range fields in the frame. These Ack Ranges are modeled as objects which contain
                two pieces of data: gap and ack_range_length. See class AckRange for implementation.
            First ACK Range:
                The next 4 bytes is the first Ack range.
                The number of packets preceding the Largest Acknowledged. All of these packets are also 
                being acknowledged.
            Ack Range:
                This section consists of a number of AckRange objects which contain a gap and ack range length field.
                The gap represents the number of unacknowledged packets from the preceding range. The ack range length
                field represents the number of packets that are acknowledged preceding the gap.
    """

    def __init__(self,
                largest_acknowledged = 0,
                ack_delay = 0,
                ack_range_count = 0,
                first_ack_range = 0,
                ack_range = []):
        self.type = FT_ACK

        

        self.largest_acknowledged = largest_acknowledged
        self.ack_delay = ack_delay
        self.ack_range_count = ack_range_count
        self.first_ack_range = first_ack_range
        self.ack_range = ack_range

    def raw(self) -> bytes:
        data = b""
        return b""


class CryptoFrame:
    """
        Crypto Frame Format:
            Type:
                The first byte represents the frame type.
            Offset:
                The next 8 bytes is the byte offset in the Crypto stream.
            Length:
                The next 2 bytes is the length of the frame data in bytes.
            Data:
                The crypto data bytes.                
    """

    def __init__(self, offset=0, length=0, data=b""):

        check_long_type("offset", offset)
        check_short_type("length", length)        

        self.type = FT_CRYPTO
        self.offset = offset
        self.length = length
        self.data = data

    def raw(self) -> bytes:
        return struct.pack("!BQH", self.type, self.offset, self.length) + self.data
    
    def __repr__(self) -> str:
        representation = ""
        representation += "------ FRAME ------\n"
        representation += f"Type: {frame_type_hex_to_string(self.type)}\n"
        representation += f"Offset: {self.offset}\n"
        representation += f"Length: {self.length}\n"
        representation += f"Data: {self.data}"
        return representation


class StreamFrame:
    """
        StreamFrame format:
            Type:
                First Byte of the frame. Identifies the frame type.
            Stream ID:
                Second Byte of the frame. Identifies the stream.
            Offset:
                The next 8 bytes are the byte offset for the data in this stream frame.
                It needs to support large values
            Length:
                The next 2 bytes are the length (number of bytes) of the stream data contained in the stream frame.
            Stream Data:
                The stream bytes to be delivered at the given offset value in the identified stream.
    """

    def __init__(self, stream_id = 0, offset = 0, length = 0, data = b""):

        check_char_type("stream_id", stream_id)
        check_long_type("offset", offset)
        check_short_type("length", length)
        
        self.type = FT_STREAM
        self.stream_id = stream_id
        self.offset = offset
        self.length = length
        self.data = data

    def raw(self):
        return struct.pack("!BBQH", self.type, self.stream_id, self.offset, self.length) + self.data

    def __repr__(self) -> str:
        representation = ""
        representation += "------ FRAME ------\n"
        representation += f"Type: {frame_type_hex_to_string(self.type)}\n"
        representation += f"Stream ID: {self.stream_id}\n"
        representation += f"Offset: {self.offset}\n"
        representation += f"Length: {self.length}\n"
        representation += f"Data: {self.data}"
        return representation


class PaddingFrame:
    """
        PaddingFrame class, a padding frame contains a single field:
            Type:
                The first byte is the type. The type field indicates the type of the frame.
                Padding frames are identified as an empty byte 0x00. 
    """

    def __init__(self):
        self.type = FT_PADDING

    def raw(self):
        return struct.pack("!B", self.type)


# class ResetStreamFrame:

#     def __init__(self, stream_id=b"", error_code=b"", final_size=b""):
#         self.type = FT_RESETSTREAM
#         self.stream_id = stream_id
#         self.error_code = error_code
#         self.final_size = final_size

#     def raw(self):
#         return self.type + self.stream_id + self.error_code + self.final_size


# class StopSendingFrame:

#     def __init__(self, stream_id=b"", error_code=b""):
#         self.type = FT_STOPSENDING
#         self.stream_id = stream_id
#         self.error_code = error_code

#     def raw(self):
#         return self.type + self.stream_id + self.error_code


# class MaxDataFrame:

#     def __init__(self, max_data=b""):
#         self.type = FT_MAXDATA
#         self.max_data = max_data

#     def raw(self):
#         return self.type + self.max_data

# class MaxStreamDataFrame:

#     def __init__(self, stream_id=b"", max_stream_data=b""):
#         self.type = FT_MAXSTREAMDATA
#         self.stream_id = stream_id
#         self.max_stream_data = max_stream_data

#     def raw(self):
#         return self.type + self.stream_id + self.max_stream_data

# class MaxStreamsFrame:

#     def __init__(self, max_streams=b""):
#         self.type = FT_MAXSTREAMS
#         self.max_streams = max_streams

#     def raw(self):
#         return self.type + self.max_streams

# class DataBlockedFrame:

#     def __init__(self, max_data=b""):
#         self.type = FT_DATABLOCKED
#         self.max_data = max_data

#     def raw(self):
#         return self.type + self.max_data

# class StreamDataBlockedFrame:

#     def __init__(self, stream_id=b"", max_stream_data=b""):
#         self.type = FT_STREAMDATABLOCKED
#         self.stream_id = stream_id
#         self.max_stream_data = max_stream_data

#     def raw(self):
#         return self.type + self.stream_id + self.max_stream_data

# class StreamsBlockedFrame:

#     def __init__(self, max_streams=b""):
#         self.type = FT_STREAMSBLOCKED
#         self.max_streams = max_streams

#     def raw(self):
#         return self.type + self.max_streams

# class ConnectionCloseFrame:

#     def __init__(self, error_code=b"", reason_phrase_len=b"", reason_phrase=b""):
#         self.type = FT_CONNECTIONCLOSE
#         self.error_code = error_code
#         self.reason_phrase_len = reason_phrase_len
#         self.reason_phrase = reason_phrase

#     def raw(self):
#         return self.type + self.error_code + self.reason_phrase_len + self.reason_phrase

# class HandshakeDoneFrame:

#     def __init__(self):
#         self.type = FT_HANDSHAKEDONE

#     def raw(self):
#         return self.type


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

        # If type_to_hex returns None, then type argument is invalid.
        type_check = header_type_string_to_hex(type)
        if type_check == None:
            print(f"Invalid long header type received: {type}")
            exit(1)

        check_int_type("destination_connection_id", destination_connection_id)
        check_int_type("source_connection_id", source_connection_id)
        check_int_type("packet_number", packet_number)

        self.header_form = HF_LONG
        self.type = type
        self.version = QUIC_VERSION
        self.destination_connection_id_len = CONN_ID_LEN
        self.destination_connection_id = destination_connection_id
        self.source_connection_id_len = CONN_ID_LEN
        self.source_connection_id = source_connection_id
        self.packet_number_length = PKT_NUM_LEN
        self.packet_number = packet_number
        self.length = 0x0000 # 0x0000 to 0xFFFF


    def raw(self) -> bytes:
        """
            Returns the header as raw bytes in network byte order.
        """
        first_byte = self.header_form | header_type_string_to_hex(self.type)
        raw_bytes = struct.pack("!BBBLBLBLH", first_byte, self.version, self.destination_connection_id_len, self.destination_connection_id, self.source_connection_id_len, self.source_connection_id, self.packet_number_length, self.packet_number, self.length)
        return raw_bytes


    def __repr__(self) -> str:
        representation = "------ HEADER ------\n"
        representation += "Header Form: Long Header\n"
        representation += f"Type: {self.type} ({header_type_string_to_hex(self.type)})\n"
        representation += f"Version: {self.version}\n"
        representation += f"Destination Connection ID Length: {self.destination_connection_id_len}\n"
        representation += f"Destination Connection ID: {self.destination_connection_id}\n"
        representation += f"Source Connection ID Length: {self.source_connection_id_len}\n"
        representation += f"Source Connection ID: {self.source_connection_id}\n"
        representation += f"Packet Number Length: {self.packet_number_length}\n"
        representation += f"Packet Number: {self.packet_number}\n"
        representation += f"Payload Length: {self.length}"
        return representation


class ShortHeader():
    """
        ShortHeader can only have 1 type which is a 1RTT packet or Data packet.
        It contains only the destination connection ID instead of source and destination
        since the destination connection ID is used to identify the connection after
        the handshake is performed.
    """

    def __init__(self, destination_connection_id, packet_number):

        check_int_type("destination_connection_id", destination_connection_id)
        check_int_type("packet_number", packet_number)

        self.type = HT_DATA
        self.destination_connection_id = destination_connection_id       # 4 bytes
        self.packet_number = packet_number                               # 4 bytes


    def raw(self)  -> bytes:
        return struct.pack("!BLL", self.type, self.destination_connection_id, self.packet_number)


    def __repr__(self) -> str:
        representation = ""
        representation = "------ HEADER ------\n"
        representation += f"Header Form: Short Header\n"
        representation += f"Type: Data ({self.type})\n"
        representation += f"Destination Connection ID: {self.destination_connection_id}\n"
        representation += f"Packet Number: {self.packet_number}"
        return representation

