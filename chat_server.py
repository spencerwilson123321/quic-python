from QUIC import QUICSocket
from database import Database
from threading import Lock, Thread
import time


class ChatServer:


    SHUTDOWN = False


    def __init__(self, ip: str, port: int):
        self.listener = QUICSocket(ip)
        self.listener.listen(port)
        self.id = 0
        self.clients = {}
        self.threads: list[Thread] = []
        self.database = Database()


    def create_new_client_id(self):
        self.id += 1
        return self.id


    def client_thread_handler(self, client: QUICSocket, client_id: int):
        disconnected = False
        username = b""
        username_received = False
        while not disconnected and not self.SHUTDOWN:
            # time.sleep(0.5)
            if not username_received:
                username, disconnected = client.recv(1, 20)
                if len(username) > 0: 
                    print(f"Received username: {username}")
                    username_received = True
            _, disconnected = client.recv(1, 1024)
        disconnected = False
        username = b""
        username_received = False
        client.release()
        print("Closing thread...")


    def mainloop(self):
        """
        """
        print("Starting mainloop...")
        while True:
            client = self.listener.accept()
            print("Connection accepted...")
            client_id = self.create_new_client_id()
            self.clients[client_id] = client
            client_thread = Thread(target=self.client_thread_handler, args=(client, client_id,))
            client_thread.start()
            print(f"Thread {client_thread.native_id} started...")
            self.threads.append(client_thread)


    def shutdown(self):
        self.SHUTDOWN = True
        print("\nShutting down threads...")
        for thread in self.threads:
            thread.join()
            print(f"Thread {thread.native_id} finished...")
        print("Shutting down server...")
        self.listener.release()


# Start with a basic multi-threaded server.
if __name__ == "__main__":

    server = ChatServer("10.0.0.131", 8000)
    try:
        server.mainloop()
    except KeyboardInterrupt:
        server.shutdown()
