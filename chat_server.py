from QUIC import QUICSocket
from database import Database
from threading import Thread, Lock
from select import poll, EPOLLIN
from ipaddress import ip_address
import argparse


PARSER = argparse.ArgumentParser(prog="chat_server.py", description="A Chat Server which uses the QUIC protocol.")
PARSER.add_argument("ip", help="The IPv4 address of this machine.")
PARSER.add_argument("port", help="The port to run the application on.")
ARGS = PARSER.parse_args()


class ChatServer:


    SHUTDOWN = False


    def __init__(self, ip: str, port: int):
        self.listener = QUICSocket(ip)
        self.listener.listen(port)
        self.clients = {}
        self.threads: list[Thread] = []
        self.database = Database()
        self.poller = poll()
        self.db_lock = Lock()
        self.client_lock = Lock()
    
    
    def create_account(self, username: str, password: str) -> bool:
        result: bool = self.database.add(username, password)
        return result
    

    def sign_in(self, username: str, password: str) -> bool:
        result: bool = self.database.exists(username, password)
        return result


    def epoll_thread_handler(self):
        while not self.SHUTDOWN:
            events = self.poller.poll(5000)
            for fd, event in events:
                if event and EPOLLIN:
                    self.client_lock.acquire()
                    data, status = self.clients[fd][0].recv(1, 1024)
                    if status:
                        # Client has closed the connection.
                        # Unregister the socket.
                        # Release the socket.
                        # Remove from the client's list.
                        print("Closing client connection...")
                        self.poller.unregister(fd)
                        self.clients[fd][0].release()
                        self.clients.pop(fd)
                    if data:
                        username: str = self.clients[fd][1]
                        data = username.encode("utf-8") + b": " + data
                        for key in self.clients:
                            if key != fd:
                                self.clients[key][0].send(1, data)
                    self.client_lock.release()


    def mainloop(self):
        """
        """
        print("Starting epoll thread... (this handles broadcasting client messages.)")
        self.epoll_thread = Thread(target=self.epoll_thread_handler)
        self.epoll_thread.start()
        print("Starting mainloop...")
        while True:
            client = self.listener.accept()
            print("Connection accepted...")
            
            # Initially the main thread will handle the new connection.
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
                client.close()

            if reason == "sign in":
                self.db_lock.acquire()
                result: bool = self.sign_in(username, password)
                self.db_lock.release()
                if result:
                    client.send(1, b"success")
                    self.client_lock.acquire()
                    self.clients[client._socket.fileno()] = (client, username)
                    self.poller.register(client._socket.fileno())
                    self.client_lock.release()
                else:
                    client.send(1, b"fail")


    def shutdown(self):
        self.SHUTDOWN = True
        print("\nShutting down threads...")
        for thread in self.threads:
            thread.join()
            print(f"Thread {thread.native_id} finished...")
        print("Shutting down epoll thread...")
        self.epoll_thread.join()
        print("Shutting down server...")
        self.listener.release()


if __name__ == "__main__":

    ip = ARGS.ip
    port = ARGS.port

    try:
        ip_address(ip)
    except ValueError:
        print(f"ERROR: Invalid IPv4 address - {ip}")
        exit(1)
    
    try:
        port = int(port)
    except ValueError:
        print(f"ERROR: Port must be an integer - {port}")
        exit(1)

    server = ChatServer(ip, port)
    try:
        server.mainloop()
    except KeyboardInterrupt:
        server.shutdown()
