import pika
from threading import Thread


class Chat:
    def __init__(self, name):
        self.name = name
        self.messages = []


class Client:
    def __init__(self):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        self.active_chat = None
        self.chats = {}
        self.channel = channel

        consuming = Thread(channel.start_consuming)
        consuming.start()

    def send_message(self, message):
        if self.active_chat is None:
            exit(0)

        self.channel.basic_publish(exchange=self.active_chat, routing_key='', body=message)

    def switch_to_chat(self, chat_name):
        self.channel.exchange_declare(chat_name)

        if chat_name not in self.chats:
            self.chats[chat_name] = Chat(chat_name)

        self.active_chat = self.chats[chat_name]

        result = self.channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        self.channel.queue_bind(exchange=chat_name, queue=queue_name)

    def read_message(self, ch, method, properties, body):
        return
