from typing import List
"""
    This module will contain code which makes it simple to
    create QUIC packets as needed. Essentially it is an 
    abstraction layer for packet creation which will be
    used in the QUICSocket module.
"""

from .QUICPacket import *

class QUICPacketBuilder:
    """
        The QUICPacketBuilder class will contain all of the necessary logic
        for creating packets which are correct and meet the contraints
        of each packet format i.e. error checking such as if a user tries
        to put a value of 300 in a 4 bit field and so on.
    """

    def __init__(self):
        pass

    def create_packet(self, frame_types: List[str], header_type) -> Packet:
        frames = self.create_frames(frame_types)
        header = self.create_header(header_type)
        return Packet(frames=frames, header=header)
    
    def create_header(self, header_type: str) -> LongHeader or ShortHeader:
        pass

    # def create_initial_packet(self) -> Packet:
    #     pass

    # def create_handshake_packet(self) -> Packet:
    #     pass

    # def create_data_packet(self) -> Packet:
    #     data_packet = Packet()
    #     data_packet.frames = [StreamFrame()]
    #     data_packet.header = ShortHeader()
    #     return data_packet
    
    # def create_ack_packet(self) -> Packet:
    #     return Packet()

    def parse_bytes(self, raw: bytes):
        """
            This parses the packet from raw bytes and returns
            a Packet object.
        """
        return Packet()

if __name__ == "__main__":
    builder = QUICPacketBuilder()
    conn_state  = {}
    pkt = builder.create_packet(frame_types=['stream'], header_form='short', header_type="1rtt", connection_state=conn_state)
