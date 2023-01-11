"""
    This module contains code for converting bytes
    into QUIC packets.    
"""

from .QUICPacket import *

def parse_packet(raw: bytes) -> Packet:
    return Packet()
