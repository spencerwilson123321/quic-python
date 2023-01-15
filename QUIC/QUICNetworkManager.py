from enum import Enum
from socket import socket, AF_INET, SOCK_DGRAM, SO_REUSEADDR, SOL_SOCKET, error
from typing import List
import errno

from .QUICConnection import ConnectionContext
from .QUICEncryption import EncryptionContext
from .QUICPacketParser import parse_packet_bytes
from .QUICSocket import QUICSocket
from .QUICPacket import *


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

SocketError = error


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
        # self.__encryption_context = EncryptionContext()
        self.__udp_socket = socket(AF_INET, SOCK_DGRAM)
        self.__udp_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.__udp_socket.setblocking(1)
    

    def __parse_packets_in_udp_buffer(self) -> list[Packet]:
        packets = []
        self.__udp_socket.recvfrom(1024)
        # raw_bytes = b""
        # while True:
        #     try:
        #         self.__udp_socket.recvfrom(1024)
        #     except SocketError as e:
        #         print(e)
        #         break
        return packets


    def create_connection(self, address: tuple):

        # 1. Create the INITIAL QUIC packet --> Create connection ID.
        self.__connection_context.set_peer_address(address)
        peer_address = self.__connection_context.get_peer_address()
        # self.__udp_socket.connect(peer_address) # so the kernel 5 tuple correctly identifies the connection.
        pkt_num = self.__connection_context.get_next_packet_number()
        conn_id = self.__connection_context.generate_connection_id()
        # TODO: Add a secret key to the crypto frame so that the connection can be encrypted.
        frames = [CryptoFrame(offset=0, length=0, data=b"")] 
        header = LongHeader(type=HT_INITIAL, destination_connection_id=0, source_connection_id=conn_id, packet_number=pkt_num)
        initial_packet = Packet(header=header, frames=frames)

        # 2. Send the INITIAL QUIC packet.  --> Transmit the bytes.
        self.__udp_socket.sendto(initial_packet.raw(), peer_address)
        local_address = self.__udp_socket.getsockname()
        self.__connection_context.set_local_address(local_address)
        received_packets = self.__parse_packets_in_udp_buffer()

        # 3. Get the server response: HANDSHAKE packet and INITIAL packet. --> parse bytes and process.
            # 3.1. Set all connection context variables that are necessary.
        

        # 4. Send the final HANDSHAKE packet to finish the handshake.
        # 5. The connection is now established.

    def accept_conenction(self):
        pass

