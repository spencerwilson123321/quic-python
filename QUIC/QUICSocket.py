"""
    This will be the public facing QUIC Sockets API which
    will have a similar API to the Python standard library
    socket object. This API will make it simple to implement
    QUIC servers and clients in Python.
"""


from socket import socket, AF_INET, SOCK_DGRAM, SO_REUSEADDR, SOL_SOCKET
from QUICConnection import ConnectionContext


class QUICSocket:


    def __init__(self, connection_context=ConnectionContext()):
        self.__socket = socket(AF_INET, SOCK_DGRAM)
        self.__socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.__connection_context = connection_context


    def connect(self, address: tuple):
        """
            This function will:
                1. Associate the given address with the underlying UDP socket using it's connect call.
                2. Perform the QUIC handshake.
        """
        print(f"Connecting to server at: {address[0]}:{address[1]}")
        self.__socket.sendto(b"HANDSHAKE #1", address)
        _, addr = self.__socket.recvfrom(1024)
        print(addr)
        print(f"Handshake complete!")


    def accept(self):
        """
            Accepts a client connection. This is done by blocking and waiting for an
            initial packet to be received on the listening socket. Once the initial
            packet is received, a connection context is created, and the handshake process
            begins. Once the connection negotation / handshake is complete, a new socket
            is created which is in a connected state (connected to client) which can then be
            used for data transfer using QUIC Streams. This function returns the newly created
            socket.
        """
        
        # Block and wait for an initial packet to be received.
        initial_packet_received = False
        addr = None
        pkt = None
        while not initial_packet_received:
            pkt, addr = self.__socket.recvfrom(1024)
            if pkt: # TODO if the pkt is indeed an initial packet, then exit the loop and proceed.
                initial_packet_received = True
        
        # TODO perform handshake code, initialize the connection context, use actual QUIC packets.
        print(f"Initial packet from: {addr[0]}:{addr[1]}")
        self.__socket.sendto(b"Handshake packet", addr)
        connection_context = ConnectionContext() # TODO fill in this class with data.

        # AFTER the handshake is complete do the following:
        # Create new QUIC socket which will be used to communicate with the connected client.
        # This can be done by creating a new QUIC socket object and associating it's underlying
        # UDP socket with the address of the connected client. We also pass the created connection
        # context to this new QUIC socket so that it can manage its own connection state.
        client = QUICSocket(connection_context=connection_context)
        client.bind(("10.0.0.159", 8001)) # Bind the socket to the server address.
        client.__socket.connect(addr)     # This 'connect' call is on the underlying UDP socket so that the kernel can track the connection properly.
        return client


    def listen(self, backlog: int):
        self.__is_listening = True


    def bind(self, address):
        self.__socket.bind(address)
        self.__is_server = True


    def close(self):
        print("Closing socket.")
        self.__socket.close()


    def set_connection_context(self, connection_context):
        self.__connection_context = connection_context


if __name__ == "__main__":
    server_addr = ("", 8001)
    sock = QUICSocket()
    sock.bind(server_addr)
    sock.listen(5)
    client = sock.accept()
