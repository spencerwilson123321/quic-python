

from .QUICConnection import ConnectionContext
from .QUICEncryption import EncryptionContext

class QUICConnectionManager:

    def __init__(self) -> None:
        self.__connection_context = ConnectionContext()
        self.__encryption_context = EncryptionContext()
    
    def handshake(self, addr):
        pass

