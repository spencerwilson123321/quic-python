"""
    This module will implement all the logic for the QUIC
    protocol and will act as abstraction layer for use
    in the QUIC socket API. Therefore the QUIC Socket 
    itself isn't maintaining the actual underyling network
    logic and instead only needs to worry about read, 
    write, connect, and close operations at a high level.
"""

class QUICProtocol:
    """
        This class will be a Finite State Machine that
        models the behaviour of the QUIC protocol.
    """

    def __init__(self):
        pass


