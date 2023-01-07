from typing import List
"""
    This module will contain code which makes it simple to
    create QUIC packets as needed. Essentially it is an 
    abstraction layer for packet creation which will be
    used in the QUICSocket module.
"""

from .QUICPacket import *

class QUICPacketParser:
    """
        The QUICPacketParser class contains functions for
        parsing and creating QUIC packets from raw bytes.
    """

    def __init__(self):
        pass

    def parse_bytes(self, raw: bytes):
        """
            This parses the packet from raw bytes and returns
            a Packet object.
        """
        return Packet()
