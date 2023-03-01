from tkinter import Tk, Frame, Entry, Label, Button, Text, END
from QUIC import QUICSocket


class InformationEntryView(Frame):
    
    def __init__(self, **kwargs):
        super().__init__(height=100, width=500, **kwargs)

        self.ip_label = Label(master=self, text="IPv4").grid(row=0, column=0, padx=10, pady=5)
        self.port_label = Label(master=self, text="Port").grid(row=0, column=1, padx=10, pady=5)
        self.username_label = Label(master=self, text="Username").grid(row=0, column=2, padx=10, pady=5)
        self.password_label = Label(master=self, text="Password").grid(row=0, column=3, padx=10, pady=5)
        
        self.ip_entry = Entry(master=self, width=10)
        self.port_entry = Entry(master=self, width=10)
        self.username_entry = Entry(master=self, width=10)
        self.password_entry = Entry(master=self, width=10)

        self.ip_entry.grid(row=1, column=0, padx=10, pady=5)
        self.port_entry.grid(row=1, column=1, padx=10, pady=5)
        self.username_entry.grid(row=1, column=2, padx=10, pady=5)
        self.password_entry.grid(row=1, column=3, padx=10, pady=5)

        self.grid(row=0, column=0, padx=5, pady=5)


class ButtonPanelView(Frame):
    
    def __init__(self, **kwargs):
        super().__init__(height=100, width=500, **kwargs)

        self.disconnect_button = Button(master=self, text="Disconnect")
        self.connect_button = Button(master=self, text="Sign In")
        self.create_account_button = Button(master=self, text="Create Account")

        self.create_account_button.grid(row=0, column=0, padx=10, pady=5)
        self.disconnect_button.grid(row=0, column=1, padx=10, pady=5)
        self.connect_button.grid(row=0, column=2, padx=10, pady=5)

        self.grid(row=1, column=0, padx=5, pady=5)


class ChatView(Frame):

    def __init__(self, **kwargs):
        super().__init__(height=300, width=500, **kwargs)
        self.chat = Text(master=self, height=16, width=60, state="disabled")
        self.grid_propagate(False)
        self.chat.grid(row=0, column=0, padx=5, pady=5)
        self.grid(row=2, column=0, sticky="w")


class MessageView(Frame):

    def __init__(self, **kwargs):
        super().__init__(height=100, width=500, **kwargs)
        self.message_entry = Text(master=self, height=4, width=50)
        self.send_button = Button(master=self, text="Send")
        self.grid_propagate(False)
        self.message_entry.grid(row=0, column=0, padx=5, pady=5)
        self.send_button.grid(row=0, column=1, padx=5, pady=5)
        self.grid(row=3, column=0)


class ChatClient:

    def __init__(self, ip: str):
        self.socket = QUICSocket(ip)

    def create_account(self) -> int:
        pass

    def sign_in(self, address: tuple[str, int], display_name: str) -> int:
        # 1. Attempt to create a connection to the QUIC server.
        #   - Could fail.
        # 2. Once connected, send the user's display name to the server.
        # TODO implement for real.
        self.socket.connect(address)
        self.socket.send(1, display_name.encode("utf-8"))
    
    def disconnect(self) -> None:
        self.socket.close()


class ChatApplication:


    def __init__(self, ip: str) -> None:

        self.connected = False
        self.ip = ip

        self.chat_client = ChatClient(ip)
        self.window = Tk()
        self.window.resizable(False, False)
        self.window.title("QUIC-Chat")
        self.content = Frame(self.window)
        self.content.grid(row=0, column=0)

        self.information_entry_view = InformationEntryView(master=self.content)
        self.button_panel_view = ButtonPanelView(master=self.content)
        self.chatview = ChatView(master=self.content)
        self.messageview = MessageView(master=self.content)

        # Event bindings.
        self.button_panel_view.bind('<Button-1>', self.on_click_create_account)
        self.button_panel_view.connect_button.bind('<Button-1>', self.on_click_connect)
        self.button_panel_view.disconnect_button.bind('<Button-1>', self.on_click_disconnect)
        self.messageview.send_button.bind('<Button-1>', self.on_click_send)


    def run(self):
        self.window.mainloop()


    def on_click_create_account(self, event):
        print("Creating account...")


    def on_click_connect(self, event):
        if self.connected:
            return None
        ip, port, display_name = self.connectionview.ip_entry.get(), self.connectionview.port_entry.get(), self.connectionview.username_entry.get()
        # TODO Verify user input.
        # IPv4 - Cannot be empty, must be a proper IPv4 address.
        # Port - Must be empty or a valid integer between 0-65535
        # Display Name - Must not be empty, cannot be longer than 12 characters.

        # Assume inputs are correct.
        self.chat_client.sign_in((ip, int(port)), display_name)
        self.connected = True


    def on_click_disconnect(self, event):
        print("Disconnecting...")
        self.chat_client.disconnect()
        self.connected = False
        self.chatview.chat.delete(0, END)
        # Create a new chat client.
        self.chat_client = ChatClient(self.ip)


    def on_click_send(self, event):
        print("Sending Message")


if __name__ == "__main__":

    application = ChatApplication("10.0.0.159")
    application.run()

