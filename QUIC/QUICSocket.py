from socket import socket, AF_INET, SOCK_DGRAM, SO_REUSEADDR, SOL_SOCKET
from .QUICConnection import ConnectionContext, create_connection_id
from .QUICEncryption import EncryptionContext
from .QUICPacketParser import parse_packet_bytes, PacketParserError
from .QUICPacket import *


class QUICListener:

    def __init__(self, address: tuple):
        self._listening_socket = socket(AF_INET, SOCK_DGRAM)
        self._listening_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self._server_address = address
        self._listening_socket.bind(address)


    def accept(self):
        return accept_connection(self._listening_socket)


class QUICSocket:

    def __init__(self):
        self._socket = socket(AF_INET, SOCK_DGRAM)
        self._socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self._connection_context = ConnectionContext()
        self._encryption_context = EncryptionContext()


    def send(self, stream_id: int, data: bytes): 
        pass


    def recv(self, stream_id: int, num_bytes: int):
        pass


    def shutdown(self):
        print("Shutting down socket...")
        self._socket.close()


    def close_stream(self, stream_id: int):
        pass


    def create_stream(self, stream_id: int):
        pass


    def set_encryption_state(self, encryption_state: EncryptionContext):
        self._encryption_context = encryption_state


    def get_encryption_state(self):
        return self._encryption_context


    def set_connection_state(self, connection_state: ConnectionContext):
        self._connection_context = connection_state


    def get_connection_state(self):
        return self._connection_context


    def get_udp_socket(self):
        return self._socket
    

    def set_udp_socket(self, new_socket: socket):
        self._socket = new_socket
    
    
    def __repr__(self) -> str:
        representation = ""
        representation += f"------ QUIC Socket ------\n"
        representation += f"Local Address: {self._connection_context.get_local_address()}\n"
        representation += f"Peer Address: {self._connection_context.get_local_address()}\n"
        representation += f"Connection Status: {'Connected' if self._connection_context.is_connected() else 'Not Connected'}\n"
        return representation


def create_connection(address: tuple) -> QUICSocket:

    # Create a new QUICSocket object.
    new_socket = QUICSocket()
    connection_state = ConnectionContext()
    encryption_state = EncryptionContext()
    udp_socket = new_socket.get_udp_socket()

    # Create the INITIAL QUIC packet and generate local connection ID.
    connection_state.set_peer_address(address)
    peer_address = connection_state.get_peer_address()
    conn_id = create_connection_id()
    connection_state.set_local_connection_id(conn_id)

    # TODO: Add a secret key to the crypto frame so that the connection can be encrypted.
    frames = [CryptoFrame(offset=0, length=0, data=b"")] 
    header = LongHeader(type=HT_INITIAL, destination_connection_id=0, source_connection_id=conn_id, packet_number=connection_state.get_next_packet_number())
    initial_packet = Packet(header=header, frames=frames)

    # Send the INITIAL QUIC packet.
    udp_socket.sendto(initial_packet.raw(), peer_address)
    local_address = udp_socket.getsockname()
    connection_state.set_local_address(local_address)

    # Get INITIAL and HANDSHAKE packets in response.
    #   - Check that we received both the INITIAL and HANDSHAKE packets.
    #   - Set our peer connection ID based on the source connection ID of the received packets
    response1 = udp_socket.recv(4096)
    response2 = udp_socket.recv(4096)
    first_packet = parse_packet_bytes(response1)
    second_packet = parse_packet_bytes(response2)
    received_initial = False
    received_handshake = False
    for pkt in [first_packet, second_packet]:
        if pkt.header.type == HT_INITIAL:
            connection_state.set_peer_connection_id(pkt.header.source_connection_id)
            received_initial = True
        if pkt.header.type == HT_HANDSHAKE:
            received_handshake = True
    if not received_handshake or not received_initial:
        print("Handshake error.")
        exit(1)

    # 4. Send the final HANDSHAKE packet to finish the handshake.
    header = LongHeader(type=HT_HANDSHAKE, destination_connection_id=1024, source_connection_id=1024, packet_number=connection_state.get_next_packet_number())
    final_handshake = Packet(header=header, frames=[])
    udp_socket.sendto(final_handshake.raw(), peer_address)

    # 5. The connection is now established.
    connection_state.set_connected(True)

    # Set the state of the newly created socket
    # and return it to the API caller.
    new_socket.set_connection_state(connection_state)
    new_socket.set_encryption_state(encryption_state)
    new_socket.set_udp_socket(udp_socket)
    return new_socket


def accept_connection(listening_socket: socket):
    """
        This function should accept a connection and return 
        a new QUICSocket for the connection.
    """

    # Create a new connection context for this new connection.
    new_socket = QUICSocket()
    connection_state = ConnectionContext()
    encryption_state = EncryptionContext()

    # Read a datagram from the UDP socket.
    packet_bytes, addr = new_socket.get_udp_socket().recvfrom(4096)
    
    # Try to parse the bytes, if it fails then this likely was not a QUIC packet.
    try:
        packet = parse_packet_bytes(packet_bytes)
    except PacketParserError:
        print("Not a QUIC packet.")

    # Check if the packet is an initial type packet.
    if packet.header.type != HT_INITIAL:
        print("Not an initial packet.")
        exit(1)
    
    # Set the peer connection ID in the connection context
    # to the source connection ID of the initial packet.
    connection_state.set_peer_connection_id(packet.header.source_connection_id)
    connection_state.set_local_connection_id(create_connection_id())
    print(listening_socket.getsockname())

    return QUICSocket()


