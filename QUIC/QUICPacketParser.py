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
    return LongHeader(type=fields[0], destination_connection_id=fields[3], source_connection_id=fields[5], packet_number=fields[7])


def parse_short_header(raw: bytes) -> ShortHeader:
    header_bytes = raw[0:SHORT_HEADER_SIZE]
    fields = struct.unpack("!BII", header_bytes)
    return ShortHeader(destination_connection_id=fields[1], packet_number=fields[2])


def parse_stream_frame(raw: bytes):
    field_data = raw[0:STREAM_FRAME_SIZE]
    fields = struct.unpack("!BBQH", field_data)
    stream_data_len = fields[3]
    stream_data = raw[STREAM_FRAME_SIZE:STREAM_FRAME_SIZE+stream_data_len]
    return StreamFrame(stream_id=fields[1], offset=fields[2], length=fields[3], data=stream_data)


def parse_ack_frame(raw: bytes):
    return AckFrame()


def parse_crypto_frame(raw: bytes):
    field_data = raw[0:CRYPTO_FRAME_SIZE]
    fields = struct.unpack("!BQH", field_data)
    crypto_data_length = fields[2]
    crypto_data = raw[CRYPTO_FRAME_SIZE:CRYPTO_FRAME_SIZE+crypto_data_length]
    return CryptoFrame(offset=fields[1], length=fields[2], data=crypto_data)


def parse_frames(raw: bytes):

    # If we receive 0 bytes then return an empty list of frames.
    if not bytes:
        return [] 
    
    frames = []
    bytes_to_process = raw
    while bytes_to_process:
        frame_type = struct.unpack("!B", bytes_to_process[0:1])[0]
        if frame_type == FT_STREAM:
            f = parse_stream_frame(bytes_to_process)
            bytes_to_process = bytes_to_process[len(f.raw()):]
            frames.append(f)
            continue
        if frame_type == FT_ACK:
            f = parse_ack_frame(bytes_to_process)
            bytes_to_process = bytes_to_process[len(f.raw()):]
            frames.append(f)
            continue
        if frame_type == FT_CRYPTO:
            f = parse_crypto_frame(bytes_to_process)
            bytes_to_process = bytes_to_process[len(f.raw()):]
            frames.append(f)
            continue
    return frames


def parse_packet_bytes(raw: bytes) -> Packet:
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
    
    frames = parse_frames(raw[header.size:])

    return Packet(header=header, frames=frames)
