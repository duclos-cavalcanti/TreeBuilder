class TreeNode():
    def __init__(self, addr:str):
        self.addr = addr
        self.ip   = addr.split(":")[0]
        self.port = addr.split(":")[1]

class Tree():
    def __init__(self, root:str, total:int, ):
        self.n      = 0
        self.total  = total

        tnode = TreeNode(root)

        self.nodes  = [ tnode ]
        self.leaves = [ tnode ]

    def set_node(self, addr:str, idx:int):
        self.nodes[idx] = TreeNode(addr)

    def next_leaf(self):
        l = self.leaves[0]
        self.leaves.pop(0)
        return l.addr

    def add_leaf(self):
        pass


