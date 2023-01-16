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
        self.peer_address = None
        self.local_address = None
        self.peer_connection_id = None
        self.local_connection_id = None
        self.connected = False
        
    
    def set_peer_connection_id(self, conn_id: int):
        self.peer_connection_id = conn_id
    

    def get_peer_connection_id(self):
        return self.peer_connection_id

    
    def set_local_connection_id(self, conn_id: int):
        self.local_connection_id = conn_id

    
    def get_local_connection_id(self):
        return self.local_connection_id


    def set_peer_address(self, addr):
        self.peer_address = addr
    

    def get_peer_address(self):
        return self.peer_address    


    def set_local_address(self, addr):
        self.local_address = addr 


    def get_local_address(self):
        return self.local_address
    

    def is_connected(self):
        return self.connected


    def set_connected(self, value: bool):
        self.connected = value

