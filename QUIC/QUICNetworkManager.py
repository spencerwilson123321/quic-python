from enum import Enum
from socket import socket, AF_INET, SOCK_DGRAM

from .QUICConnection import ConnectionContext
from .QUICEncryption import EncryptionContext
from .QUICPacketParser import parse_packet_bytes
from .QUICSocket import QUICSocket


# class Stream:

#     def __init__(self, stream_id: int):
#         self.buffer = b""
#         self.stream_id = stream_id

    
# class StreamManager:

#     def __init_(self):
#         self.__streams = []

#     def write_to_stream(self):
#         pass

#     def read_from_stream(self):
#         pass


class QUICNetworkManager:
    """
        TODO:
        1. Implement code for performing handshakes without congestion control code.
            1.1. Create the client-side code for connecting to a server.
            1.2. Create the server-side code for accepting connections from the client.
        
        2. Implement code for reading and writing to sockets that are connected (After the handshake.)
        3. Implement congestion control for sockets while they are in the connected state.
        4. Implement encryption in the handshake and encrypt all bytes after the handshake is done.
    """

    def __init__(self) -> None:
        self.__connection_context = ConnectionContext()
        self.__encryption_context = EncryptionContext()
        # self.__stream_manager = StreamManager()
        self.__udp_socket = socket(AF_INET, SOCK_DGRAM)


    def create_connection(self, server_address: tuple):
        self.__connection_context.set_peer_address(server_address)
        # 1. Create the INITIAL QUIC packet --> Choose connection ID.
        # 2. Send the INITIAL QUIC packet.  --> Transmit the bytes.
        # 3. Get the server response: HANDSHAKE packet and INITIAL packet. --> parse bytes and process.
            # 3.1. Set all connection context variables that are necessary.
        # 4. Send the final HANDSHAKE packet to finish the handshake.
        # 5. The connection is now established.

    def accept_conenction(self):
        pass

