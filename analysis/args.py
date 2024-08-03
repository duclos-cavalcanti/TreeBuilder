class Args():
    def __init__(self, x:int=0, y:int=0, w:int=0, h:int=0, 
                       f:int=8, nf:int=0, tf:int=0, 
                       s:int=0, tbfont:int=8, factor:float=0.5):
        self.x      = x
        self.y      = y
        self.w      = w
        self.h      = h
        self.font   = f
        self.nfont  = nf
        self.tfont  = tf
        self.size   = s
        self.legend = True 
        self.title  = True 
        self.xlabel = True 
        self.ylabel = True 
        self.factor = factor
        self.tbfont = tbfont
