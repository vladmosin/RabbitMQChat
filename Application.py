import argparse
import datetime
from tkinter import N, S, W, E, Grid
from tkinter import Tk, StringVar, Entry, Frame, END, BOTH, Scrollbar, Listbox, Button, simpledialog, YES, ttk
from threading import Lock

from MessageSubscriber import MessageSubscriber
from client import Client


class ChatWindow(MessageSubscriber):
    def __init__(self, root, username, client: Client):
        self.client = client
        self.frame = Frame(root)
        self.username = username
        self.put_message_lock = Lock()

        self.channel_name_to_messages = dict()
        self.channel_name_to_input_field = dict()
        self.channel_name_to_input_user = dict()

        Grid.columnconfigure(self.frame, 0, weight=2)
        Grid.columnconfigure(self.frame, 1, weight=0)
        Grid.rowconfigure(self.frame, 0, weight=2)
        Grid.rowconfigure(self.frame, 1, weight=0)

        self.tab_parent = ttk.Notebook(self.frame)
        self.tab_parent.grid(row=0, column=0)

        self.configure_tab('1 channel')
        self.configure_tab('2 channel')

        self.frame.pack(fill=BOTH, expand=YES)

        self.put_message_in_channel('1 channel', 'Hello world!', 'Vasya')

    def configure_tab(self, channel_name):
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

    def put_message_in_channel(self, channel_name, message, username, color="red"):
        with self.put_message_lock:
            messages = self.channel_name_to_messages[channel_name]
            messages.insert(END, username + ": " + message)
            messages.itemconfig(END, {"fg": color})
            messages.yview(END)

    def send_message(self, channel_name):
        input_value = self.channel_name_to_input_field[channel_name].get()
        self.channel_name_to_input_user[channel_name].set('')
        print(f'Send into: {channel_name}. Message: {input_value}')


def start_client():
    root = Tk()
    root.title("MQ Rabbit Chat")
    root.withdraw()
    username = simpledialog.askstring("Username", "What's your name", parent=root)
    if username is None:
        return
    root.deiconify()
    client = Client(username)
    chat_window = ChatWindow(root, username, client)
    root.mainloop()


if __name__ == "__main__":
    start_client()
