from random import randrange
"""
    This module will contain the ConnectionContext class which
    will contain all of the data and state for a connection.
"""

MAX_CONNECTION_ID = 4294967295

def create_connection_id():
    return randrange(MAX_CONNECTION_ID)


class ConnectionContext:


    def __init__(self) -> None:
        self.peer_address: tuple = ()
        self.local_address: tuple = ()
        self.local_ip: str = ""
        self.local_port: int = 0
        self.peer_connection_id: int = 0
        self.local_connection_id: int = 0
        self.connected: bool = False
    
    def update_local_address(self) -> None:
        self.local_address = (self.local_ip, self.local_port)

    def set_local_port(self, port: int) -> None:
        self.local_port = port

    def get_local_port(self) -> int:
        return self.local_port

    def set_local_ip(self, ip: str) -> None:
        self.local_ip = ip

    def get_local_ip(self) -> str:
        return self.local_ip    

    def set_peer_connection_id(self, conn_id: int) -> None:
        self.peer_connection_id = conn_id

    def get_peer_connection_id(self) -> int:
        return self.peer_connection_id

    
    def set_local_connection_id(self, conn_id: int) -> None:
        self.local_connection_id = conn_id

    
    def get_local_connection_id(self) -> int:
        return self.local_connection_id


    def set_peer_address(self, addr) -> None:
        self.peer_address = addr
    

    def get_peer_address(self) -> tuple[str, int]:
        return self.peer_address


    def set_local_address(self, addr) -> None:
        self.local_address = addr 


    def get_local_address(self) -> tuple[str, int]:
        return self.local_address
    

    def is_connected(self) -> bool:
        return self.connected


    def set_connected(self, value: bool) -> None:
        self.connected = value

