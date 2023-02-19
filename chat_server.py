from QUIC import QUICSocket
from threading import Lock, Thread, get_ident


class ChatServer:

    def __init__(self, ip: str, port: int):
        self.listener = QUICSocket(ip)
        self.listener.listen(port)

        self.threads = []
        self.clients = []


    def client_thread_handler(self, client: QUICSocket):
        print(f"Thread {get_ident()} started...")
        client.close()
        print(f"Closing thread {get_ident()}...")


    def mainloop(self):
        """
        """
        print("Starting mainloop...")
        while True:
            client = self.listener.accept()
            print("Connection accepted...")
            client_thread = Thread(target=self.client_thread_handler, args=(self, client,))
            client_thread.start()
            self.threads.append(client_thread)
            self.clients.append(client)


    def shutdown(self):
        print("\nShutting down server...")



# Start with a basic multi-threaded server.
if __name__ == "__main__":

    server = ChatServer("10.0.0.159", 8000)
    try:
        server.mainloop()
    except KeyboardInterrupt:
        server.shutdown()
