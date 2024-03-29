"""
    QUIC Packet module. Contains all classes that
    are used to represent QUIC packets. Contains
    header and frame classes.
"""
import struct


# ------------------ DATA --------------------------

# DATA SIZES:
MAX_LONG = 18446744073709551615   # 8 bytes max - Use Q in struct.pack
MAX_INT = 4294967295              # 4 bytes max - Use I in struct.pack
MAX_SHORT = 65535                 # 2 bytes max - Use H in struct.pack
MAX_CHAR = 255                    # 1 byte max  - Use B in struct.pack

HT_INITIAL = 0xC0 # 11000000
HT_0RTT = 0xD0 # 11010000
HT_HANDSHAKE = 0xE0 # 11100000
HT_RETRY = 0xF0 # 11110000
HT_DATA = 0x40 # 0100 0000

LONG_HEADER_SIZE = 19 # num bytes
SHORT_HEADER_SIZE = 9 # num bytes

STREAM_FRAME_SIZE = 12 # Not including stream data.
CRYPTO_FRAME_SIZE = 11 # Not including crypto data.
ACK_FRAME_SIZE = 17    # Not including the ack range field.
ACK_RANGE_SIZE = 8     # Size of a single ack range.
CONNECTION_CLOSE_FRAME_SIZE = 3

QUIC_VERSION = 0x01
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

class InvalidArgumentException(Exception): pass


# ------------------ FUNCTIONS ------------------


def check_long_type(var_name: str, var: int) -> None:
    if var < 0:
        raise InvalidArgumentException(f"Variable '{var_name}' cannot be negative. '{var_name}' value: {var}")
    if var > MAX_LONG:
        raise InvalidArgumentException(f"Variable '{var_name}' cannot be greater than {MAX_LONG}. '{var_name}' value: {var}")
    return None


def check_int_type(var_name: str, var: int) -> None:
    if var < 0:
        raise InvalidArgumentException(f"Variable '{var_name}' cannot be negative. '{var_name}' value: {var}")
    if var > MAX_INT:
        raise InvalidArgumentException(f"Variable '{var_name}' cannot be greater than {MAX_INT}. '{var_name}' value: {var}")
    return None


def check_short_type(var_name: str, var: int) -> None:
    if var < 0:
        raise InvalidArgumentException(f"Variable '{var_name}' cannot be negative. '{var_name}' value: {var}")
    if var > MAX_SHORT:
        raise InvalidArgumentException(f"Variable '{var_name}' cannot be greater than {MAX_SHORT}. '{var_name}' value: {var}")
    return None


def check_char_type(var_name: str, var: int) -> None:
    if var < 0:
        raise InvalidArgumentException(f"Variable '{var_name}' cannot be negative. '{var_name}' value: {var}")
    if var > MAX_CHAR:
        raise InvalidArgumentException(f"Variable '{var_name}' cannot be greater than {MAX_CHAR}. '{var_name}' value: {var}")
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

        if not isinstance(gap, int) or isinstance(gap, bool):
            raise TypeError("gap must be of type int.")
        
        if not isinstance(ack_range_length, int) or isinstance(ack_range_length, bool):
            raise TypeError("ack_range_length must be of type int.")

        check_int_type("gap", gap)
        check_int_type("ack_range_length", ack_range_length)

        self.gap = gap
        self.ack_range_length = ack_range_length

    def __repr__(self) -> str:
        return f"Gap: {self.gap}\nAck Range Length: {self.ack_range_length}"

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

        if not isinstance(largest_acknowledged, int) or isinstance(largest_acknowledged, bool):
            raise TypeError("largest_acknowledged must be of type int.")
        
        if not isinstance(ack_delay, int) or isinstance(ack_delay, bool):
            raise TypeError("ack_delay must be of type int.")
        
        if not isinstance(ack_range_count, int) or isinstance(ack_range_count, bool):
            raise TypeError("ack_range_count must be of type int.")
        
        if not isinstance(first_ack_range, int) or isinstance(first_ack_range, bool):
            raise TypeError("first_ack_range must be of type int.")
        
        if not isinstance(ack_range, list):
            raise TypeError("ack_range must be of type list.")


        check_int_type("largest_acknowledged", largest_acknowledged)
        check_int_type("ack_delay", ack_delay)
        check_int_type("ack_range_count", ack_range_count)
        check_int_type("first_ack_range", first_ack_range)

        self.type = FT_ACK
        self.largest_acknowledged = largest_acknowledged
        self.ack_delay = ack_delay
        self.ack_range_count = ack_range_count
        self.first_ack_range = first_ack_range
        self.ack_range = ack_range

    def raw(self) -> bytes:
        data = struct.pack("!BIIII", self.type, self.largest_acknowledged, self.ack_delay, self.ack_range_count, self.first_ack_range)
        for ar in self.ack_range:
            data += ar.raw()
        return data

    def __repr__(self) -> str:
        representation = ""
        representation += "------ FRAME ------\n"
        representation += f"Type: {frame_type_hex_to_string(self.type)}\n"
        representation += f"Largest Acknowledged: {self.largest_acknowledged}\n"
        representation += f"First Ack Range: {self.first_ack_range}\n"
        representation += f"ACK Delay: {self.ack_delay}\n"
        representation += f"ACK Range Count: {self.ack_range_count}\n"
        if self.ack_range_count > 0:
            for range in self.ack_range:
                representation += "------ ACK RANGE ------\n"
                representation += f"Gap: {range.gap}\n"
                representation += f"Ack Range Length: {range.ack_range_length}\n"
        return representation


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

        if not isinstance(offset, int) or isinstance(offset, bool):
            raise TypeError("offset must be of type int.")
        
        if not isinstance(length, int) or isinstance(length, bool):
            raise TypeError("length must be of type int.")
        
        if not isinstance(data, bytes):
            raise TypeError("data must be of type bytes.")

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

        if not isinstance(stream_id, int) or isinstance(stream_id, bool):
            raise TypeError("stream_id must be of type int.")
        
        if not isinstance(offset, int) or isinstance(offset, bool):
            raise TypeError("offset must be of type int.")
        
        if not isinstance(length, int) or isinstance(length, bool):
            raise TypeError("length must be of type int.")
        
        if not isinstance(data, bytes):
            raise TypeError("data must be of type bytes.")

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

class ConnectionCloseFrame:

    """
        Type - First Byte.
        Error Code - Second Byte.
        Reason Phrase Len - Third Byte.
        Reason Phrase - bytes of defined length.
    """

    def __init__(self, error_code=0, reason_phrase_len=0, reason_phrase=b""):
        self.type = FT_CONNECTIONCLOSE

        if not isinstance(error_code, int) or isinstance(error_code, bool):
            raise TypeError("error_code must be of type int.")
        
        if not isinstance(reason_phrase_len, int) or isinstance(reason_phrase_len, bool):
            raise TypeError("reason_phrase_len must be of type int.")

        check_char_type("error code", error_code)
        check_char_type("reason_phrase_len", reason_phrase_len)

        self.error_code = error_code
        self.reason_phrase_len = reason_phrase_len
        self.reason_phrase = reason_phrase
    

    def __repr__(self) -> str:
        representation = ""
        representation += "------ FRAME ------\n"
        representation += f"Type: {frame_type_hex_to_string(self.type)}\n"
        representation += f"Error Code: {self.error_code}\n"
        representation += f"Reason Phrase Length: {self.reason_phrase_len}\n"
        representation += f"Reason Phrase: {self.reason_phrase}"
        return representation

    def raw(self):
        return struct.pack("!BBB", self.type, self.error_code, self.reason_phrase_len) + self.reason_phrase


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
                type=0,
                destination_connection_id=0,
                source_connection_id=0,
                packet_number=0
                ):

        if not isinstance(destination_connection_id, int):
            raise TypeError(f"destination_connection_id expected type int but got type {type(destination_connection_id)}")

        if not isinstance(source_connection_id, int):
            raise TypeError(f"source_connection_id expected type int but got type {type(source_connection_id)}")

        if not isinstance(packet_number, int):
            raise TypeError(f"packet_number expected type int but got type {type(packet_number)}")

        if type not in [HT_INITIAL, HT_HANDSHAKE, HT_RETRY]:
            raise(InvalidArgumentException(f"Invalid long header type received: {type}"))

        check_int_type("destination_connection_id", destination_connection_id)
        check_int_type("source_connection_id", source_connection_id)
        check_int_type("packet_number", packet_number)

        self.type = type
        self.version = QUIC_VERSION
        self.destination_connection_id_len = CONN_ID_LEN
        self.destination_connection_id = destination_connection_id
        self.source_connection_id_len = CONN_ID_LEN
        self.source_connection_id = source_connection_id
        self.packet_number_length = PKT_NUM_LEN
        self.packet_number = packet_number
        self.length = 0x0000 # 0x0000 to 0xFFFF
        self.size = LONG_HEADER_SIZE


    def raw(self) -> bytes:
        """
            Returns the header as raw bytes in network byte order.
        """
        raw_bytes = struct.pack("!BBBIBIBIH", self.type, self.version, self.destination_connection_id_len, self.destination_connection_id, self.source_connection_id_len, self.source_connection_id, self.packet_number_length, self.packet_number, self.length)
        return raw_bytes


    def __repr__(self) -> str:
        representation = "------ HEADER ------\n"
        representation += "Header Form: Long Header\n"
        representation += f"Type: {self.type} ({header_type_hex_to_string(self.type)})\n"
        representation += f"Version: {self.version}\n"
        representation += f"Destination Connection ID Length: {self.destination_connection_id_len}\n"
        representation += f"Destination Connection ID: {self.destination_connection_id}\n"
        representation += f"Source Connection ID Length: {self.source_connection_id_len}\n"
        representation += f"Source Connection ID: {self.source_connection_id}\n"
        representation += f"Packet Number Length: {self.packet_number_length}\n"
        representation += f"Packet Number: {self.packet_number}\n"
        representation += f"Payload Length: {self.length}"
        return representation


class ShortHeader:
    """
        ShortHeader can only have 1 type which is a 1RTT packet or Data packet.
        It contains only the destination connection ID instead of source and destination
        since the destination connection ID is used to identify the connection after
        the handshake is performed.
    """

    def __init__(self, destination_connection_id: int, packet_number: int):

        if not isinstance(destination_connection_id, int):
            raise TypeError(f"destination_connection_id expected type int but got type {type(destination_connection_id)}")
        
        if isinstance(destination_connection_id, bool):
            raise TypeError(f"destination_connection_id expected type int but got type {type(destination_connection_id)}")

        if not isinstance(packet_number, int):
            raise TypeError(f"packet_number expected type int but got type {type(packet_number)}")

        if isinstance(packet_number, bool):
            raise TypeError(f"packet_number expected type int but got type {type(packet_number)}")

        check_int_type("destination_connection_id", destination_connection_id)
        check_int_type("packet_number", packet_number)

        self.type = HT_DATA
        self.destination_connection_id = destination_connection_id       # 4 bytes
        self.packet_number = packet_number                               # 4 bytes
        self.size = SHORT_HEADER_SIZE


    def raw(self)  -> bytes:
        return struct.pack("!BII", self.type, self.destination_connection_id, self.packet_number)


    def __repr__(self) -> str:
        representation = ""
        representation = "------ HEADER ------\n"
        representation += f"Header Form: Short Header\n"
        representation += f"Type: Data ({self.type})\n"
        representation += f"Destination Connection ID: {self.destination_connection_id}\n"
        representation += f"Packet Number: {self.packet_number}"
        return representation

