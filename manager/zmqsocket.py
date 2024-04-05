import zmq

class Socket():
    def __init__(self, type):
        self.context = zmq.Context()
        self.socket  = self.context.socket(type)

    def recv(self, *args, **kwargs):
        return self.socket.recv(*args, **kwargs)

    def send(self, *args, **kwargs):
        return self.socket.send(*args, **kwargs)

    def recv_json(self, *args, **kwargs):
        return self.socket.recv_json(*args, **kwargs)

    def send_json(self, *args, **kwargs):
        return self.socket.send_json(*args, **kwargs)

    def recv_string(self, *args, **kwargs):
        return self.socket.recv_string(*args, **kwargs)

    def send_string(self, *args, **kwargs):
        return self.socket.send_string(*args, **kwargs)

class ReplySocket(Socket):
    def __init__(self, protocol:str, ip:str, port:str):
        self.format = f"{protocol}://{ip}:{port}"
        super().__init__(zmq.REP)

    def bind(self):
        self.socket.bind(self.format)

class RequestSocket(Socket):
    def __init__(self):
        super().__init__(zmq.REQ)
