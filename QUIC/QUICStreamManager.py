from .QUICNetworkController import QUICSenderSideController



class QUICStreamReceiveBuffer:

    
    def __init__(self):
        self._sender_side_controller = QUICSenderSideController()

    
    def read_from_stream(self, stream_id: int, num_bytes: int):
        pass


    def write_to_stream(self, stream_id: int, data: bytes):
        self._sender_side_controller.send_data()
