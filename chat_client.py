from tkinter import Tk, Frame
from QUIC import QUICSocket

class LoginView(Frame):

    def __init__(self, **kwargs):
        super().__init__(width=500, height=500, **kwargs)
        self.pack()


if __name__ == "__main__":
    # window = Tk()
    # window.geometry("500x500")
    # window.title("QUIC-Chat")
    # login = LoginView(master=window)
    # window.mainloop()
    client = QUICSocket("10.0.0.159")
    client.connect(("10.0.0.131", 8000))
    data, connected = client.recv(1, 1024)
    client.release()

