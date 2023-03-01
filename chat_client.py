from tkinter import Tk, Frame, Entry, Label, Button, Text, END
from QUIC import QUICSocket
from ipaddress import ip_address


def pad(input: str, pad_length: int) -> str:
    while len(input) < pad_length:
        input += " "
    return input


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


    def create_account(self, ip: str, port: int, username: str, password: str) -> int:
        reason = pad("create", 12)
        self.socket.connect((ip, port))
        self.socket.send(1, reason.encode("utf-8"))
        self.socket.send(1, username.encode("utf-8"))
        self.socket.send(1, password.encode("utf-8"))
        response = b""
        while not response:
            response, status = self.socket.recv(1, 12)
        response = response.decode("utf-8")
        response = response.strip()
        if response == "success":
            return "Account created successfully."
        elif response == "fail":
            return "Could not create account, username and password already exist."


    def sign_in(self, ip: str, port: int, username: str, password: str) -> bool:
        self.socket.connect((ip, port))
        self.socket.send(1, username.encode("utf-8"))
        self.socket.send(1, password.encode("utf-8"))
        return True
    

    def disconnect(self) -> None:
        self.socket.close()


class ChatApplication:


    def __init__(self, ip: str) -> None:

        self.signed_in = False
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
        self.button_panel_view.create_account_button.bind('<Button-1>', self.on_click_create_account)
        self.button_panel_view.connect_button.bind('<Button-1>', self.on_click_sign_in)
        self.button_panel_view.disconnect_button.bind('<Button-1>', self.on_click_disconnect)
        self.messageview.send_button.bind('<Button-1>', self.on_click_send)


    def run(self):
        self.window.mainloop()
    

    def validate_inputs(self, ip: str, port: str, username: str, password: str) -> bool:
        try:
            ip_address(ip)
        except ValueError:
            self.write_message_to_console("Invalid IP address, try again.")
            return False
        try:
            port = int(port)
            if port < 1 or port > 65535:
                raise ValueError
        except ValueError:
            self.write_message_to_console("'port' must be an integer between 1 and 65535.")
            return False
        if len(username) == 0 or len(username) > 12:
            self.write_message_to_console("Username cannot be empty or greater than 12 characters.")
            return False
        if len(password) == 0 or len(password) > 12:
            self.write_message_to_console("Password cannot be empty or greater than 12 characters.")
            return False
        return True
    


    def write_message_to_console(self, message: str):
        self.chatview.chat.config(state="normal")
        self.chatview.chat.insert(END, message + "\n")
        self.chatview.chat.config(state="disabled")


    def get_all_entries(self) -> tuple[str, str, str, str]:
        return self.information_entry_view.ip_entry.get(), self.information_entry_view.port_entry.get(), self.information_entry_view.username_entry.get(), self.information_entry_view.password_entry.get()


    def on_click_create_account(self, event):
        if self.signed_in:
            # Can't make an account if already signed in.
            return None
        ip, port, username, password = self.get_all_entries()
        
        if not self.validate_inputs(ip, port, username, password):
            return

        # Pad username / password with whitespace so that they are both len == 12
        username = pad(username, 12)
        password = pad(password, 12)

        self.chat_client.create_account(ip, int(port), username, password)


    def on_click_sign_in(self, event):
        if self.signed_in:
            return None
        ip, port, username, password = self.get_all_entries()
        
        if not self.validate_inputs(ip, port, username, password):
            return

        # Pad username / password with whitespace so that they are both len == 12
        username = pad(username, 12)
        password = pad(password, 12)

        print("TODO: implement sign in")
        # self.connected = self.chat_client.sign_in(ip, int(port), username, password)
        

    def on_click_disconnect(self, event):
        print("Disconnecting...")
        self.chat_client.disconnect()
        self.signed_in = False
        self.chatview.chat.delete(0, END)
        # Create a new chat client.
        self.chat_client = ChatClient(self.ip)


    def on_click_send(self, event):
        print("Sending Message")


if __name__ == "__main__":

    application = ChatApplication("10.0.0.159")
    application.run()

