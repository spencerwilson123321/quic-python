"""
    This module contains code for converting bytes
    into QUIC packets.    
"""

from .QUICPacket import *


class PacketParserError(Exception): pass


def check_first_bit_set(byte: bytes) -> bool:
    mask = 0x80
    return (mask & byte) != 0
 

def parse_long_header(raw: bytes) -> LongHeader:

    return None


def parse_short_header(raw: bytes) -> ShortHeader:
    header_bytes = raw[0:SHORT_HEADER_SIZE]
    fields = struct.unpack("!BII", header_bytes)
    return ShortHeader(destination_connection_id=fields[1], packet_number=fields[2])


def parse_bytes(raw: bytes) -> Packet:
    """
        TODO: docstring
    """
    first_byte = raw[0:1]
    header_type = struct.unpack("!B", first_byte)
    packet = Packet()
    header = None
    frames = []

    if check_first_bit_set(header_type[0]):
        print("This is a long header.")
        header = parse_long_header(raw)
    else:
        print("This is a short header.")
        header = parse_short_header(raw)
        print(header)

    return packet
