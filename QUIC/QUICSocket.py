from socket import socket, AF_INET, SOCK_DGRAM, SO_REUSEADDR, SOL_SOCKET
from .QUICNetworkController import QUICNetworkController, CONNECTED


class QUICSocket:

    def __init__(self, local_ip: str):
        self._socket = socket(AF_INET, SOCK_DGRAM)
        self._socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self._network_controller = QUICNetworkController()
        self._network_controller._connection_context.set_local_ip(local_ip)


    def connect(self, address: tuple[str, int]):
        self._network_controller.create_connection(self._socket, address)


    def listen(self, port=8000):
        self._network_controller._connection_context.set_local_port(port)
        self._network_controller._connection_context.update_local_address()
        self._network_controller.listen(self._socket)


    def accept(self):
        # We give the network controller our wildcard socket.
        self._network_controller.accept_connection(self._socket)

        # When the above call is complete, the network controller's connection context will be filled out.
        # We just need  to copy it's QUICPacketizer and ConnectionContext into a new socket and then return it.
        connection = QUICSocket("")
        connection._network_controller._packetizer = self._network_controller._packetizer
        connection._network_controller._connection_context = self._network_controller._connection_context
        connection._network_controller.set_state(CONNECTED)
        return connection


    def send(self, stream_id: int, data: bytes):
        self._network_controller.send_stream_data(stream_id, data, self.get_udp_socket())


    def recv(self, stream_id: int, num_bytes: int):
        data = self._network_controller.read_stream_data(stream_id, num_bytes, self.get_udp_socket())
        return data


    def close(self):
        pass

    def close_stream(self, stream_id: int):
        pass

    def create_stream(self, stream_id: int):
        pass

    def get_connection_state(self):
        return self._network_controller.get_connection_state()

    def get_udp_socket(self):
        return self._socket

    def set_udp_socket(self, new_socket: socket):
        self._socket = new_socket


    def __repr__(self) -> str:
        connection_context = self._network_controller.get_connection_state()
        representation = ""
        representation += f"------ QUIC Socket ------\n"
        representation += f"Connection Status: {'Connected' if connection_context.is_connected() else 'Not Connected'}\n"
        representation += f"Local Address: {connection_context.get_local_address()}\n"
        representation += f"Peer Address: {connection_context.get_peer_address()}\n"
        representation += f"Local Connection ID: {connection_context.get_local_connection_id()}\n"
        representation += f"Peer Connection ID: {connection_context.get_peer_connection_id()}\n"
        return representation


def create_connection(address: tuple, local_ip_address: str) -> QUICSocket:

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
    header = LongHeader(type=HT_INITIAL, destination_connection_id=0, source_connection_id=conn_id, packet_number=0)
    initial_packet = Packet(header=header, frames=frames)

    # Send the INITIAL QUIC packet.
    udp_socket.bind((local_ip_address, udp_socket.getsockname()[1]))
    udp_socket.connect(address)
    udp_socket.sendto(initial_packet.raw(), peer_address)
    local_address = (local_ip_address, udp_socket.getsockname()[1])
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
    header = LongHeader(type=HT_HANDSHAKE, destination_connection_id=1024, source_connection_id=1024, packet_number=0)
    final_handshake = Packet(header=header, frames=[])
    udp_socket.sendto(final_handshake.raw(), peer_address)

    # 5. The connection is now established.
    connection_state.set_connected(True)

    # Set the state of the newly created socket
    # and return it to the API caller.
    new_socket.set_connection_state(connection_state)
    new_socket.set_encryption_state(encryption_state)
    new_socket.set_udp_socket(udp_socket)
    new_socket._network_controller.create_stream(stream_id = 1)
    return new_socket


class QUICListener:

    def __init__(self, address: tuple):
        self.address = address
        self.listening_socket = socket(AF_INET, SOCK_DGRAM)
        self.listening_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.listening_socket.bind(("", self.address[1]))


    def accept(self) -> QUICSocket:
        """
            This function should accept a connection and return 
            a new QUICSocket for the connection.
        """
        # Create a new connection context for this new connection.
        new_socket = QUICSocket()
        connection_state = ConnectionContext()
        encryption_state = EncryptionContext()

        # Read a datagram from the UDP socket.
        packet_bytes, addr = self.listening_socket.recvfrom(4096)
        
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
        connection_state.set_local_address(self.address)
        connection_state.set_peer_address(addr)
        connection_state.set_connected(True)

        # Create the response packets:
        initial_header = LongHeader(
            type=HT_INITIAL, 
            destination_connection_id=connection_state.peer_connection_id, 
            source_connection_id=connection_state.local_connection_id,
            packet_number=0)
        handshake_header = LongHeader(
            type=HT_HANDSHAKE,
            destination_connection_id=connection_state.peer_connection_id,
            source_connection_id=connection_state.local_connection_id,
            packet_number=0)
        packet1 = Packet(header=initial_header, frames=[])
        packet2 = Packet(header=handshake_header, frames=[])

        # Send the response packets.
        sock = new_socket.get_udp_socket()
        sock.bind(connection_state.get_local_address())
        sock.connect(connection_state.get_peer_address())
        sock.sendto(packet1.raw(), connection_state.get_peer_address())
        sock.sendto(packet2.raw(), connection_state.get_peer_address())

        # Set the connection and encryption state for the new socket.
        new_socket.set_connection_state(connection_state)
        new_socket.set_encryption_state(encryption_state)
        new_socket._network_controller.create_stream(stream_id = 1)
        return new_socket
