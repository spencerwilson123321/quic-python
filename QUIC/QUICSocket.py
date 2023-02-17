from socket import socket, AF_INET, SOCK_DGRAM, SO_REUSEADDR, SOL_SOCKET
from .QUICNetworkController import QUICNetworkController, LISTENING_INITIAL


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
        # socket, connection_context, encryption_context, buffered_packets, recv_streams, send_streams, state, packetizer = self._network_controller.accept_connection(self._socket)
        network_con: QUICNetworkController = self._network_controller.accept_connection(self._socket)
        connection = QUICSocket("")
        connection._socket = network_con.new_socket
        connection._network_controller = network_con
        connection._network_controller.create_stream(1)
        print(f"Client Encryption Key: {connection._network_controller._encryption_context.key}")

        # When the above call is complete, the network controller's connection context will be filled out.
        # We just need  to copy it's QUICPacketizer and ConnectionContext into a new socket and then return it.
        self._network_controller = QUICNetworkController()
        self._network_controller._connection_context.set_local_ip(network_con._connection_context.get_local_ip())
        self._network_controller._connection_context.set_local_port(network_con._connection_context.get_local_port())
        self._network_controller._connection_context.update_local_address()
        # Set network controller back to listening state.
        self._network_controller.state = LISTENING_INITIAL
        return connection


    def send(self, stream_id: int, data: bytes) -> int:
        return self._network_controller.send_stream_data(stream_id, data, self.get_udp_socket())


    def recv(self, stream_id: int, num_bytes: int) -> tuple[bytes, bool]:
        return self._network_controller.read_stream_data(stream_id, num_bytes, self.get_udp_socket())


    def close(self):
        """
            Issues a ConnectionClose frame to the peer and closes the connection.
            Used to inform the peer that you want to close the connection.
        """
        self._network_controller.initiate_connection_termination(self.get_udp_socket())

    def release(self):
        """
            Closes the connection without sending a ConnectionClose frame to the peer.
            Used to close a connection when a peer has issued a ConnectionClose frame.
        """
        self._network_controller.respond_to_connection_termination(self.get_udp_socket())

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

