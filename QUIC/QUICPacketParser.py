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
    header_bytes = raw[0:LONG_HEADER_SIZE]
    fields = struct.unpack(f"!BBBIBIBIH", header_bytes)
    return LongHeader(destination_connection_id=fields[3], source_connection_id=fields[5], packet_number=fields[7])


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
    header = None
    frames = []

    if check_first_bit_set(header_type[0]):
        header = parse_long_header(raw)
    else:
        header = parse_short_header(raw)

    return Packet(header=header)
