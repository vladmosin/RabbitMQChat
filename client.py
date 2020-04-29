import pika

class Chat:
    def __init__(self, name):
        self.name = name
        self.messages = []


class Client:
    def __init__(self, name, channel):
        self.active_chat = None
        self.name = name
        self.chats = []
        self.channel = channel

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

def send_message(message):
    pass


def switch_to_chat(chat_name):
    pass


def read_message(message):
    pass


if __name__ == "__main__":
    pass