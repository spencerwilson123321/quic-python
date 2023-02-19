from QUIC import QUICSocket
from database import Database
from threading import Lock, Thread
import time

class ChatServer:

    SHUTDOWN = False

    def __init__(self, ip: str, port: int):
        self.listener = QUICSocket(ip)
        self.listener.listen(port)
        self.threads: list[Thread] = []
        self.database = Database()


    def client_thread_handler(self, client: QUICSocket):
        disconnected = False
        while not disconnected and not self.SHUTDOWN:
            time.sleep(2)
        client.release()


    def mainloop(self):
        """
        """
        print("Starting mainloop...")
        while True:
            client = self.listener.accept()
            print("Connection accepted...")
            client_thread = Thread(target=self.client_thread_handler, args=(client,))
            client_thread.start()
            print(f"Thread {client_thread.ident} started...")
            self.threads.append(client_thread)


    def shutdown(self):
        self.SHUTDOWN = True
        print("\nShutting down threads...")
        for thread in self.threads:
            thread.join()
            print(f"Thread {thread.ident} finished...")
        print("Shutting down server...")
        self.listener.release()


# Start with a basic multi-threaded server.
if __name__ == "__main__":

    server = ChatServer("10.0.0.159", 8000)
    try:
        server.mainloop()
    except KeyboardInterrupt:
        server.shutdown()
