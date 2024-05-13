class TreeNode():
    def __init__(self, addr:str):
        self.addr = addr
        self.ip   = addr.split(":")[0]
        self.port = addr.split(":")[1]

class Tree():
    def __init__(self, total:int):
        self.n      = 0
        self.total  = total
        self.nodes  = []
        self.leaves = []

    def next_layer(self, idx):
        if idx == 0:
            return 2
        else:
            return 2

    def set_node(self, addr:str, idx:int):
        tnode = TreeNode(addr)
        self.nodes.append(tnode)
        self.leaves.append(tnode)

