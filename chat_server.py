from QUIC import QUICSocket
from threading import Lock


class ChatServer:

    def __init__(self, ip: str, port: int):
        self.listener = QUICSocket(ip)
        self.listener.listen(port)

        self.threads = []
        self.clients = []

    def client_thread_handler(self, client: QUICSocket):
        pass


    def mainloop(self):
        """
        """
        print("Starting mainloop...")
        while True:
            pass


    def shutdown(self):
        print("\nShutting down server...")



# Start with a basic multi-threaded server.
if __name__ == "__main__":

    server = ChatServer("10.0.0.159", 8000)
    try:
        server.mainloop()
    except KeyboardInterrupt:
        server.shutdown()
