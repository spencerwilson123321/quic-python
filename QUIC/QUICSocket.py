"""
    This will be the public facing QUIC Sockets API which
    will have a similar API to the Python standard library
    socket object. This API will make it simple to implement
    QUIC servers and clients in Python.
"""

from socket import socket, AF_INET, SOCK_DGRAM, SO_REUSEADDR, SO_REUSEPORT, SOL_SOCKET

class QUICSocket:

    def __init__(self):
        self.__socket = socket(AF_INET, SOCK_DGRAM)
        self.__socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.__socket.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        self.__is_server = False
        self.__is_listening = False

    def connect(self, address: tuple):
        """
            This function will:
                1. Associate the given address with the underlying UDP socket using it's connect call.
                2. Perform the QUIC handshake.
        """
        print(f"Connecting to server at: {address[0]}:{address[1]}")
        self.__socket.sendto(b"HANDSHAKE #1", address)
        data, addr = self.__socket.recvfrom(1024)
        print(addr)
        print(f"Handshake complete!")

    def accept(self):
        handshake, addr = self.__socket.recvfrom(1024)
        print(f"Received connection from: {addr[0]}:{addr[1]}")
        client_sock = socket(AF_INET, SOCK_DGRAM)
        client_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        client_sock.bind(("", 8001))
        client_sock.connect(addr)
        client_sock.send(b"HANDSHAKE 2")
        return client_sock, addr

    def listen(self, backlog: int):
        self.__is_listening = True

    def bind(self, address):
        self.__socket.bind(address)
        self.__is_server = True

    def close(self):
        print("Closing socket.")
        self.__socket.close()

    def send(self, data: bytes):
        pass

    def recv(self, nbytes: int):
        return self.__socket.recv(nbytes)

