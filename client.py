import pika
from threading import Thread


class Chat:
    def __init__(self, name):
        self.name = name
        self.messages = []


class Client:
    def __init__(self, name, channel):
        self.active_chat = None
        self.name = name
        self.chats = {}
        self.channel = channel

    def send_message(self, message):
        pass

    def switch_to_chat(self, chat_name):
        self.channel.exchange_declare(chat_name)

        if chat_name not in self.chats:
            self.chats[chat_name] = Chat(chat_name)

        self.active_chat = self.chats[chat_name]


    def read_message(self, message):
        pass


def get_name():
    return "Vasya"


if __name__ == "__main__":
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    name = get_name()
    client = Client(name=name, channel=channel)

    consuming = Thread(client.channel.start_consuming)
    consuming.start()
    consuming.join()