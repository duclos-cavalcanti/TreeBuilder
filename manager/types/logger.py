import logging 
import json 
import sys

from google.protobuf.json_format import MessageToDict

STATE  = 25
RECORD = 26

_logger = logging.getLogger('LOGGER')

logging.addLevelName(STATE,  "STATE")
logging.addLevelName(RECORD, "RECORD")

class Formatter(logging.Formatter):
    GREEN   = '\033[92m'
    RED     = '\033[91m'
    BLUE    = '\033[94m'
    GREY    = '\033[90m'
    YELLOW  = '\033[93m'

    def __init__(self, fmt):
        super().__init__()
        self.FORMAT = fmt
        self.CLEAR  = "\033[0m"
        self.FORMATS = {
            RECORD: self.GREEN  + self.FORMAT + self.CLEAR,
            STATE:  self.GREY   + self.FORMAT + self.CLEAR,
        }


    def format(self, record):
        if record.levelno in self.FORMATS:
            fmt = self.FORMATS.get(record.levelno)
        else:
            fmt = self.FORMAT

        formatter = logging.Formatter(fmt=fmt)
        return formatter.format(record)

class Logger():
    def __init__(self, name:str="", path:str="/volume"):
            if name: self.setup(name, path)

    def setup(self, name:str, path:str):
        format = '%(asctime)s | %(name)s:[%(levelname)s] %(message)s'
        f = logging.FileHandler(f"{path}/{name}.log", mode='w')
        f.setLevel(logging.DEBUG)
        f.setFormatter(logging.Formatter(format))

        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        ch.setFormatter(Formatter(format))

        logging.basicConfig(level=logging.DEBUG,
                            handlers=[ 
                                f, 
                                ch
                            ]
        )
    
    def info(self, message: str):
        _logger.log(logging.INFO, message)
    
    def debug(self, message: str):
        _logger.log(logging.DEBUG, message)
    
    def error(self, message: str):
        _logger.log(logging.ERROR, message)

    def state(self, message: str):
        _logger.log(STATE, message)

    def record(self, message: str):
        _logger.log(RECORD, message)


    def log(self, message: str, level=logging.INFO):
        _logger.log(level, message)
    
    def logd(self, message:str, d:dict, level=logging.INFO):
        data = json.dumps(d, indent=4)
        _logger.log(level, f"{message}: {data}")
    
    def logm(self,  message:str, m, level=logging.INFO):
        data = MessageToDict(m)
        self.logd(message, data, level)

    def flush(self):
        for handler in _logger.handlers:
            handler.flush()
