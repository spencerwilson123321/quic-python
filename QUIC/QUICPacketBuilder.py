"""
    This module will contain code which makes it simple to
    create QUIC packets as needed. Essentially it is an 
    abstraction layer for packet creation which will be
    used in the QUICSocket module.
"""

from QUICPacket import *

class QUICPacketBuilder:
    """
        The QUICPacketBuilder class will contain all of the necessary logic
        for creating packets which are correct and meet the contraints
        of each packet format i.e. error checking such as if a user tries
        to put a value of 300 in a 4 bit field and so on.
    """

    def __init__(self):
        pass

    def create_initial_packet(self):
        pass
