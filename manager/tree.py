class TreeNode():
    def __init__(self, addr:str):
        self.addr = addr
        self.ip   = addr.split(":")[0]
        self.port = addr.split(":")[1]

class Tree():
    def __init__(self, n:int):
        self.root = None
        self.n = n

    def set_root(self, addr:str):
        self.root = TreeNode(addr)

