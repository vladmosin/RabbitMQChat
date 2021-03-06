from threading import Lock
from tkinter import N, S, W, E, Grid
from tkinter import Tk, StringVar, Entry, Frame, END, BOTH, Scrollbar, Listbox, Button, simpledialog, YES, ttk

from MessageSubscriber import MessageSubscriber
from client import Client
from threading import Thread


class ChatWindow(MessageSubscriber):

    def __init__(self, root, username):
        self.client = None
        self.frame = Frame(root)
        self.username = username
        self.put_message_lock = Lock()

        self.channel_name_to_messages = dict()
        self.channel_name_to_input_field = dict()
        self.channel_name_to_input_user = dict()
        self.channels = set()

        Grid.columnconfigure(self.frame, 0, weight=2)
        Grid.columnconfigure(self.frame, 1, weight=0)
        Grid.rowconfigure(self.frame, 0, weight=2)
        Grid.rowconfigure(self.frame, 1, weight=0)
        Grid.rowconfigure(self.frame, 2, weight=0)

        self.tab_parent = ttk.Notebook(self.frame)
        self.tab_parent.grid(row=0, column=0)

        self.configure_tab('saved messages')

        self.frame.pack(fill=BOTH, expand=YES)

        self.input_channel_name = StringVar()
        self.input_channel_name_field = Entry(self.frame, text=self.input_channel_name)
        self.input_channel_name_field.grid(row=2, column=0, sticky=W+E+S)
        self.subscribe_button = Button(self.frame, text="Subscribe", command=self.subscribe)
        self.subscribe_button.grid(row=2, column=0, sticky=S + E)

    def subscribe(self):
        channel_name = self.input_channel_name_field.get()
        self.input_channel_name.set('')
        self.client.switch_to_chat(channel_name)
        if channel_name not in self.channels:
            self.configure_tab(channel_name)

    def configure_tab(self, channel_name):
        self.channels.add(channel_name)

        tab = ttk.Frame(self.tab_parent)
        self.tab_parent.add(tab, text=channel_name)

        scrollbar = Scrollbar(tab)

        messages = Listbox(tab, yscrollcommand=scrollbar.set, height=15, width=50)
        messages.grid(row=0, column=0, sticky=N + S + W + E)
        self.channel_name_to_messages[channel_name] = messages

        scrollbar.grid(row=0, column=1, sticky=N + S)
        scrollbar.config(command=messages.yview)

        input_user = StringVar()
        self.channel_name_to_input_user[channel_name] = input_user

        input_field = Entry(tab, text=input_user)
        input_field.grid(row=1, column=0, sticky=W+E+S)
        self.channel_name_to_input_field[channel_name] = input_field

        send_button = Button(tab, text="Send", command=lambda: self.send_message(channel_name))
        send_button.grid(row=1, column=1, sticky=S)

        input_field.bind("<Return>", lambda key: self.send_message(channel_name))

        input_field.focus()

    def put_message_in_channel(self, channel_name, message, color="red"):
        with self.put_message_lock:
            messages = self.channel_name_to_messages[channel_name]
            messages.insert(END, message)
            messages.itemconfig(END, {"fg": color})
            messages.yview(END)

    def send_message(self, channel_name):
        input_value = self.channel_name_to_input_field[channel_name].get()
        message = f'{self.username}: {input_value}'
        self.channel_name_to_input_user[channel_name].set('')
        self.client.send_message_to_chat(message, channel_name)

    def receive_message(self, text, channel):
        self.put_message_in_channel(channel, text)


def start_client():
    root = Tk()
    root.title("MQ Rabbit Chat")
    root.withdraw()
    username = simpledialog.askstring("Username", "What's your name", parent=root)
    if username is None:
        return
    root.deiconify()
    chat_window = ChatWindow(root, username)
    client = Client(chat_window)
    chat_window.client = client
    root.mainloop()


if __name__ == "__main__":
    start_client()
