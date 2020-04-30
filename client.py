import pika
from threading import Thread, Lock
import random


class Chat:
    def __init__(self, name):
        self.name = name
        self.messages = []


class Client:
    def __init__(self, message_subscriber):
        self.active_chat = None
        self.chats = {}
        self.message_subscriber = message_subscriber
        self.lock = Lock()

        self.queue_name = None
        self.queue_init()

        consuming = Thread(target=self.reading, daemon=True)
        consuming.start()

    def queue_init(self):
        with pika.BlockingConnection(pika.ConnectionParameters(host='localhost')) as connection:
            channel = connection.channel()
            self.queue_name = str(random.getrandbits(128))
            channel.queue_declare(queue=self.queue_name)

    def send_message_to_chat(self, message, chat_name):
        self.switch_to_chat(chat_name)
        self.send_message(message)

    def send_message(self, message):
        if self.active_chat is None:
            return
        with pika.BlockingConnection(pika.ConnectionParameters(host='localhost')) as connection:
            channel = connection.channel()
            channel.basic_publish(exchange=self.active_chat, routing_key=self.queue_name, body=message)

    def switch_to_chat(self, chat_name):
        with pika.BlockingConnection(pika.ConnectionParameters(host='localhost')) as connection:
            channel = connection.channel()

            if chat_name not in self.chats:
                self.chats[chat_name] = Chat(chat_name)

            channel.exchange_declare(exchange=chat_name, exchange_type='fanout')
            self.active_chat = self.chats[chat_name].name
            channel.queue_bind(exchange=chat_name, queue=self.queue_name)

    def read_message(self, ch, method, properties, body):
        self.message_subscriber.receive_message(body, method.exchange)

    def reading(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.basic_consume(queue=self.queue_name, on_message_callback=self.read_message, auto_ack=True)
        channel.start_consuming()
