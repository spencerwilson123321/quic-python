from tkinter import Tk, Frame, Entry, Label, Button, Text, Message, Scrollbar
from QUIC import QUICSocket


class ConnectionView(Frame):
    
    def __init__(self, **kwargs):
        super().__init__(height=100, width=500, **kwargs)

        self.ip_label = Label(master=self, text="IPv4").grid(row=0, column=0, padx=10, pady=5)
        self.port_label = Label(master=self, text="Port").grid(row=0, column=1, padx=10, pady=5)
        self.display_name_label = Label(master=self, text="Display Name").grid(row=0, column=2, padx=10, pady=5)
        
        self.ip_entry = Entry(master=self, width=10)
        self.port_entry = Entry(master=self, width=10)
        self.display_name_entry = Entry(master=self, width=10)
        
        self.ip_entry.grid(row=1, column=0, padx=10, pady=5)
        self.port_entry.grid(row=1, column=1, padx=10, pady=5)
        self.display_name_entry.grid(row=1, column=2, padx=10, pady=5)

        self.disconnect_button = Button(master=self, text="Disconnect")
        self.connect_button = Button(master=self, text="Connect")
        
        self.disconnect_button.grid(row=0, column=3, padx=10, pady=5)
        self.connect_button.grid(row=1, column=3, padx=10, pady=5)

        self.grid(row=0, column=0, padx=5, pady=5)


class ChatView(Frame):

    def __init__(self, **kwargs):
        super().__init__(background="grey", height=300, width=500, **kwargs)
        self.chat = Text(master=self, height=16, width=60, state="disabled")
        self.grid_propagate(False)
        self.chat.grid(row=0, column=0, padx=5, pady=5)
        self.grid(row=1, column=0, sticky="w")


class MessageView(Frame):

    def __init__(self, **kwargs):
        super().__init__(background="grey", height=100, width=500, **kwargs)
        self.message_entry = Text(master=self, height=4, width=50)
        self.send_button = Button(master=self, text="Send")
        self.grid_propagate(False)
        self.message_entry.grid(row=0, column=0, padx=5, pady=5)
        self.send_button.grid(row=0, column=1, padx=5, pady=5)
        self.grid(row=2, column=0)


class ChatClient:


    def __init__(self, ip: str):
        self.socket = QUICSocket(ip)


    def create_connection(self, address: tuple[str, int], display_name: str) -> None:
        # 1. Attempt to create a connection to the QUIC server.
        #   - Could fail.
        # 2. Once connected, send the user's display name to the server.
        # TODO implement for real.
        self.socket.connect(address)
        self.socket.send(1, display_name.encode("utf-8"))
        self.socket.release()


class ChatApplication:


    def __init__(self, ip: str) -> None:

        self.connected = False

        self.chat_client = ChatClient(ip)
        self.window = Tk()
        self.window.resizable(False, False)
        self.window.title("QUIC-Chat")
        self.content = Frame(self.window)
        self.content.grid(row=0, column=0)

        self.connectionview = ConnectionView(master=self.content)
        self.chatview = ChatView(master=self.content)
        self.messageview = MessageView(master=self.content)

        # Event bindings.
        self.connectionview.connect_button.bind('<Button-1>', self.connect)
        self.connectionview.disconnect_button.bind('<Button-1>', self.disconnect)
        self.messageview.send_button.bind('<Button-1>', self.send_message)


    def run(self):
        self.window.mainloop()


    def connect(self, event):
        if self.connected:
            return None
        ip, port, display_name = self.connectionview.ip_entry.get(), self.connectionview.port_entry.get(), self.connectionview.display_name_entry.get()
        # TODO Verify user input.
        # IPv4 - Cannot be empty, must be a proper IPv4 address.
        # Port - Must be empty or a valid integer between 0-65535
        # Display Name - Must not be empty, cannot be longer than 12 characters.

        # Assume inputs are correct.
        self.chat_client.create_connection((ip, int(port)), display_name)
        self.connected = True


    def disconnect(self, event):
        print("Disconnected")


    def send_message(self, event):
        print("Sending Message")


if __name__ == "__main__":

    # client = QUICSocket("10.0.0.159")
    # client.connect(("10.0.0.131", 8000))
    # data, connected = client.recv(1, 1024)
    # client.release()

    # window = Tk()
    # window.resizable(False, False)
    # window.title("QUIC-Chat")
    # window.config(bg="skyblue")
    # content = Frame(window)
    # content.grid(row=0, column=0)

    # connectionview = ConnectionView(master=content)
    # chatview = ChatView(master=content)
    # messageview = MessageView(master=content)

    # window.mainloop()


    application = ChatApplication("10.0.0.159")
    application.run()

