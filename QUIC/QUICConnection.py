"""
    This module will contain the ConnectionContext class which
    will contain all of the data and state for a connection.
"""

class ConnectionContext:
    """
            
    """


    def __init__(self, peer_address=None, local_address=None, is_connected=False) -> None:
        self.peer_address = peer_address
        self.local_address = local_address
        self.is_connected = is_connected
        self.next_packet_number = 1
    

    def set_peer_address(self, addr):
        self.peer_address = addr
    

    def get_peer_address(self):
        return self.peer_address    


    def set_local_address(self, addr):
        self.local_address = addr 


    def get_local_address(self, addr):
        return self.peer_address    


    def get_next_packet_number(self) -> int:
        num = self.next_packet_number
        self.next_packet_number += 1
        return num

    def generate_connection_id(self) -> int:
        """
            This function generates a random connection ID.
            TODO: Implement this function.
        """
        return 1024

