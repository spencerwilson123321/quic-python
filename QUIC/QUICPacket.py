"""
    QUIC Packet module. Contains all classes that
    are used to represent QUIC packets.
"""
import struct


# ------------------ DATA --------------------------


# HEADER INFO:
LONG_HEADER_FORM = 0x80
SHORT_HEADER_FORM = 0x00
QUIC_VERSION = 0x36
CONN_ID_LEN = 0x04
PKT_NUM_LEN = 0x04
MAX_CONN_ID = 4294967295
MAX_PKT_NUM = 4294967295


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


# FRAME TYPE --> String
frame_type_string_map = {
    FT_STREAM: "Stream",
    FT_ACK: "Acknowledgement",
    FT_CRYPTO: "Crypto"
}


# ------------------ CLASSES/FUNCTIONS ------------------


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
        representation = ""
        representation += f"{self.header}\n"
        for frame in self.frames:
            representation += frame.__repr__() + "\n"
        return representation


class AckRange:
    """
        An ACK Range 
    """

    def __init__(self, gap, ack_range_length) -> None:
        self.gap = gap
        self.ack_range_length = ack_range_length
    
    def raw(self) -> bytes:
        return b""


class AckFrame:
    """
        ACK Frame Format:
            Type:
                The first byte of the frame is the type.
            Largest Acknowledged:
                the largest packet number being acknowledged.
                In other words, the largest packet number that the peer has received prior to creating
                the Ack Frame.
            ACK Delay:
                The acknowledgement delay in microseconds.
            ACK Range Count:
                The number of ack range fields in the frame. These Ack Ranges are modeled as objects which contain
                two pieces of data: gap and ack_range_length. See class AckRange for implementation.
            First ACK Range:
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
        self.type = FT_CRYPTO
        self.offset = offset
        self.length = length
        self.data = data

    def raw(self) -> bytes:
        return struct.pack("!BQH", self.type, self.offset, self.length) + self.data
    
    def __repr__(self) -> str:
        representation = ""
        representation += "------ FRAME ------\n"
        representation += f"Type: {frame_type_string_map[self.type]}\n"
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

    def __init__(self,
                stream_id = 0,
                offset = 0,
                length = 0,
                data = b""):
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
        representation += f"Type: {frame_type_string_map[self.type]}\n"
        representation += f"Stream ID: {self.stream_id}\n"
        representation += f"Offset: {self.offset}\n"
        representation += f"Length: {self.length}\n"
        representation += f"Data: {self.data}"
        return representation


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
        representation += f"Type: {self.type} ({self.type_to_hex(self.type)})\n"
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
    DATA_PKT = 0x04


    def __init__(self, destination_connection_id, packet_number):

        if destination_connection_id > MAX_CONN_ID:
            print(f"Invalid destination connection id: {destination_connection_id}.")
            print(f"Connection IDs must be less than {MAX_CONN_ID}.")
            exit(1)

        if packet_number > MAX_PKT_NUM:
            print(f"Invalid packet number: {packet_number}.")
            print(f"Packet numbers must be less than {MAX_PKT_NUM}.")
            exit(1)

        self.type = self.DATA_PKT
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

