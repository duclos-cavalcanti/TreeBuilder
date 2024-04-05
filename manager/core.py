from .zmqsocket import ReplySocket, RequestSocket

class Manager():
    def __init__(self, port="23456"):
        self.socket = ReplySocket(protocol="tcp", ip="*", port=port)


class Client():
    def __init__(self, port="23456"):
        self.socket = RequestSocket()

