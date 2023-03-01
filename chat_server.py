from QUIC import QUICSocket
from database import Database
from threading import Thread, Lock
from time import sleep


class ChatServer:


    SHUTDOWN = False


    def __init__(self, ip: str, port: int):
        self.listener = QUICSocket(ip)
        self.listener.listen(port)
        self.id = 0
        self.clients = {}
        self.threads: list[Thread] = []
        self.database = Database()
        self.db_lock = Lock()
        self.client_lock = Lock()
    
    
    def create_account(self, username: str, password: str) -> bool:
        result: bool = self.database.add(username, password)
        return result
    

    def sign_in(self, username: str, password: str) -> bool:
        result: bool = self.database.exists(username, password)
        return result


    def create_new_client_id(self):
        self.id += 1
        return self.id


    def client_thread_handler(self, client: QUICSocket, client_id: int):

        # 1. Get the reason for connection.
        reason = b""
        username = b""
        password = b""

        while not reason:
            reason, status = client.recv(1, 12)

        while not username:
            username, status = client.recv(1, 12)

        while not password:
            password, status = client.recv(1, 12)
        
        reason = reason.strip()
        username = username.strip()
        password = password.strip()

        reason = reason.decode("utf-8")
        username = username.decode("utf-8")
        password = password.decode("utf-8")

        if reason == "create":
            self.db_lock.acquire()
            result: bool = self.create_account(username, password)
            self.db_lock.release()
            if result:
                client.send(1, b"success")
            else:
                client.send(1, b"fail")
        
        if reason == "sign in":
            self.db_lock.acquire()
            result: bool = self.sign_in(username, password)
            self.db_lock.release()
            if result:
                client.send(1, b"success")
                while not status:
                    # Wait for messages from client.
                    data, status = client.recv(1, 1024)
                    if data:
                        self.client_lock.acquire()
                        for id in self.clients:
                            if id == client_id:
                                continue
                            self.clients[id].send(1, username.encode("utf-8") + b": " + data)
                        self.client_lock.release()
            else:
                client.send(1, b"fail")
        
        if status == True:
            client.release()
            self.client_lock.acquire()
            self.clients.pop(client_id)
            self.client_lock.release()
            print("Closing thread.")   
            return
        
        while status == False:
            data, status = client.recv(1, 1024)
        self.client_lock.acquire()
        self.clients.pop(client_id)
        self.client_lock.release()
        print("Closing thread.")            



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
