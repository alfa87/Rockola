"""
Messaging Queue abstraction layer. It uses a RabbitMQ sever.
"""

import pika

names = {'flask': 'flask_queue',
         'lists': 'lists_queue',
         'control': 'control_queue'}

IP = 'localhost'

def get_queue_name(queue):
    """
    Gets the name of the desired queue. This method enforces that all the
    publishers and subscribers uses the same queue name.

    :param queue: one of 'lists', 'control', 'flask'
    :returns: the name of the desired queue.
    """
    return names[queue]


class Queue(object):

    def __init__(self, queues=names.values(),
                 ip=IP):
        """
        Creates a publisher class to a message queue.

        :param queues: The list of queues
        :param ip: The IP of the RabbitMQ server.
        """
        params = pika.ConnectionParameters(host=ip, channel_max=20,
                                           connection_attempts=10,
                                           retry_delay=0.5)
        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()

        for queue in queues:
            self._declare_queue(queue)

    def __del__(self):
        """
        Closes the connection to the rabbitmq server.
        """
        self.connection.close()

    def _declare_queue(self, name):
        """
        Creates a queue in the messaging server.
        """
        self.channel.queue_declare(queue=name)

    def send(self, name, cmd):
        """
        Send a msg to the queue.

        :param cmd: The msg to send.
        """
        self.channel.basic_publish(exchange='', routing_key=name,
                                   body=cmd)

    def receive(self, name):
        """
        Blocking method to receive a message from the queue.

        :param name: The name of the desired queue.
        :param ip: The IP of the RabbitMQ server.
        """
        method = None
        while not method:
            method, header, body = self.channel.basic_get(name)
        self.channel.basic_ack(method.delivery_tag)
        return body

    def receive_no_block(self, name):
        """
        Non blocking method to receive a message from the queue.

        :param name: The name of the desired queue.
        :param ip: The IP of the RabbitMQ server.
        """
        method, header, body = self.channel.basic_get(name)
        if method:
            self.channel.basic_ack(method.delivery_tag)
            return body
        else:
            return None
