"""
    QUIC Packet module. Contains all classes that
    are used to represent each QUIC packet.
"""

# Notes:
# All number fields are in Network-Byte Order (Big Endian)

import struct


class Packet():

    def __init__(self):
        self.type = None
        self.header = None
        self.frame = None


class Frame():

    def __init__(self):
        pass


# ----------------- QUIC Long Header Format -----------------------
#  0                   1                   2                   3
#  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
# +-+-+-+-+-+-+-+-+
# |1|   Type (7)  |
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# |                                                               |
# +                       Connection ID (64)                      +
# |                                                               |
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# |                       Packet Number (32)                      |
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# |                         Version (32)                          |
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# |                          Payload (*)                        ...
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

class LongHeader():
    
    def __init__(self):
        self.header_form = None                     # 1 byte
        self.fixed_bit = None                       # 1 byte
        self.long_packet_type = None                # 2 bytes
        self.type_specific_bits = None              # 4 bytes
        self.version = None                         # 32 bytes
        self.destination_connection_id_len = None   # 8 bytes
        self.destination_connection_id = None       # 0...160 bytes
        self.source_connection_id_len = None        # 8 bytes
        self.source_connection_id = None            # 0...160 bytes
        self.packet_number_len = None               # 1 byte
        self.packet_number = None                   # 1 to 4 bytes long
        self.length = None                          # variable length integer.


# ----------------- Short Header Format ---------------------------
#  0                   1                   2                   3
#  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
# +-+-+-+-+-+-+-+-+
# |0|C|K| Type (5)|
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# |                                                               |
# +                     [Connection ID (64)]                      +
# |                                                               |
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# |                      Packet Number (8/16/32)                ...
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# |                     Protected Payload (*)                   ...
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

class ShortHeader():
    
    def __init__(self):
        self.header_form = None         # first bit of first byte
        self.connection_id_flag = None  # second bit of first byte
        self.key_phase_bit = None       # third bit of first byte
        self.type = None                # remaining 5 bits of first byte
        self.connection_id = None       # 8 bytes
        self.packet_number = None       # 1, 2, or 4 bytes long depending on the header type
