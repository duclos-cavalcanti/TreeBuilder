class PlotArgs():
    def __init__(self, x:int=0, y:int=0, w:int=0, h:int=0, 
                       f:int=8, nf:int=0, tf:int=0, 
                       s:int=0):
        self.x      = x
        self.y      = y
        self.w      = w
        self.h      = h
        self.font   = f
        self.nfont  = nf
        self.tfont  = tf
        self.size   = s
        self.red    = '#FF9999'
        self.blue   = '#99CCFF'
        self.grey   = '#CCCCCC' # #efe897

pargs = PlotArgs(w=28, h=16, f=16, nf=18, tf=24, s=2100)
