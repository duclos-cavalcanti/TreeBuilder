from .zmqsocket import ReplySocket, RequestSocket

import argparse
import time

class Manager():
    def __init__(self, ip:str, port:str):
        self.socket = ReplySocket(protocol="tcp", ip="*", port=port)

    def bind(self):
        self.socket.bind()
    
    def recv(self):
        data = self.socket.recv_string()
        return data

    def send(self, string:str):
        self.socket.send_string(string)

class Client():
    def __init__(self, ip:str, port:str):
        self.socket = RequestSocket(protocol="tcp", ip=ip, port=port)

    def connect(self):
        self.socket.connect()

    def recv(self):
        data = self.socket.recv_string()
        return data

    def send(self, string:str):
        self.socket.send_string(string)

def server(args):
    M = Manager(ip=args.addr, port=args.port) 
    M.bind()
    print(f"Bound to {args.addr}:{args.port}")

    while(True):
        data = M.recv()
        reply = f"ACK: {data}"
        print(f"Received: {data}")
        M.send(reply) 
        print(f"Sent: {reply}")

def client(args):
    C = Client(ip=args.addr, port=args.port) 
    C.connect()
    print(f"Connected to {args.addr}:{args.port}")
    i = 0
    while(True):
        data = f"Hello from {args.name} | {i}"
        C.send(data)
        print(f"Sent: {data}")
        reply = C.recv()
        print(f"Received: {reply}")
        time.sleep(1)
        i += 1

    

def parse(rem=None):
    arg_def = argparse.ArgumentParser(
        description='Module to automate terraform stack management.',
        epilog='Example: core.py -a create -m docker'
    )

    arg_def.add_argument(
        "-a", "--action",
        type=str,
        required=False,
        default="server",
        choices=["server", "client"],
        dest="action",
    )

    arg_def.add_argument(
        "-i", "--ip",
        type=str,
        required=True,
        dest="addr",
    )

    arg_def.add_argument(
        "-p", "--port",
        type=int,
        default=8081,
        required=False,
        dest="port",
    )

    arg_def.add_argument(
        "-n", "--name",
        type=str,
        required=False,
        dest="name",
    )

    if not rem: args = arg_def.parse_args()
    else: args = arg_def.parse_args(rem)

    return args

def main(rem):
    args = parse(rem)

    match args.action:
        case "server":  server(args)
        case "client":  client(args)

    return

