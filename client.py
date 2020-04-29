import pika
from threading import Thread


class Chat:
    def __init__(self, name):
        self.name = name
        self.messages = []


class Client:
    def __init__(self, message_subscriber):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        self.active_chat = None
        self.chats = {}
        self.channel = channel
        self.message_subscriber = message_subscriber

        result = channel.queue_declare(queue='', exclusive=True)
        self.queue_name = result.method.queue

        consuming = Thread(target=self.reading, daemon=True)
        consuming.start()

    def send_message(self, message):
        if self.active_chat is None:
            exit(0)

        self.channel.basic_publish(exchange=self.active_chat, routing_key='', body=message)

    def switch_to_chat(self, chat_name):
        self.channel.exchange_declare(exchange=chat_name, exchange_type='fanout')

        if chat_name not in self.chats:
            self.chats[chat_name] = Chat(chat_name)

        self.active_chat = self.chats[chat_name].name
        self.channel.queue_bind(exchange=chat_name, queue=self.queue_name)

    def read_message(self, ch, method, properties, body):
        self.message_subscriber.receive_message(body, method.exchange)

    def reading(self):
        channel = pika.BlockingConnection(pika.ConnectionParameters(host='localhost')).channel()
        while True:
            channel.basic_consume(
                queue=self.queue_name, on_message_callback=self.read_message, auto_ack=True
            )
            channel.start_consuming()