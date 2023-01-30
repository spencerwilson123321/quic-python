from socket import socket, AF_INET, SOCK_DGRAM, SO_REUSEADDR, SOL_SOCKET
from .QUICNetworkController import QUICNetworkController, CONNECTED, QUICPacketizer


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
        connection._network_controller._send_streams = self._network_controller._send_streams.copy()
        connection._network_controller._receive_streams = self._network_controller._receive_streams.copy()
        connection._socket.bind(connection._network_controller._connection_context.get_local_address())
        connection._socket.connect(connection._network_controller._connection_context.get_peer_address())

        self._network_controller._packetizer = QUICPacketizer()
        self._network_controller._send_streams = dict()
        self._network_controller._receive_streams = dict()

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

