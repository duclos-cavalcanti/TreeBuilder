import logging 
import json 
import sys

from typing import List
from google.protobuf.json_format import MessageToDict

# DEBUG = 10
EVENTS = 17
# STATS  = 18
# TREES  = 19
# INFO = 20
STATE  = 25
RECORD = 26
# WARNING = 30
# ERROR = 40

_logger = logging.getLogger('LOGGER')

logging.addLevelName(STATE,  "STATE")
logging.addLevelName(RECORD, "RECORD")
logging.addLevelName(EVENTS, "EVENT")
# logging.addLevelName(STATS,  "STATS")
# logging.addLevelName(TREES,  "TREES")

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
            STATE:  self.BLUE   + self.FORMAT + self.CLEAR,
            40:     self.RED    + self.FORMAT + self.CLEAR,
            # ERROR = 40
        }


    def format(self, record):
        if record.levelno in self.FORMATS:
            fmt = self.FORMATS.get(record.levelno)
        else:
            fmt = self.FORMAT

        formatter = logging.Formatter(fmt=fmt)
        return formatter.format(record)

class LevelFilter(logging.Filter):
    def __init__(self, levels:List):
        self.levels = levels

    def filter(self, record):
        for level in self.levels:
            if record.levelno == level:
                return True
        return False

class Logger():
    def __init__(self, name:str="", path:str="/work/logs"):
            if name: self.setup(name, path)

    def setup(self, name:str, path:str):
        """
        i)   (f)  File Handler logs from DEBUG on.
        ii)  (ch) Stream Handler logs from INFO on.
        iii) (rf) File Handler logs only EVENTS.
        """
        format = '%(asctime)s | %(name)s:[%(levelname)s] %(message)s'

        f = logging.FileHandler(f"{path}/{name}.log", mode='w')
        f.setLevel(logging.DEBUG)
        f.setFormatter(logging.Formatter(format))

        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        ch.setFormatter(Formatter(format))

        if "manager" in name:
            rf = logging.FileHandler(f"{path}/events.log", mode='w')
            rf.setLevel(EVENTS)
            rf.setFormatter(Formatter('%(message)s'))
            rf.addFilter(LevelFilter([ EVENTS ]))
            logging.basicConfig(level=logging.DEBUG, handlers=[ f, ch, rf ])

        else:
            logging.basicConfig(level=logging.DEBUG, handlers=[ f, ch ])
    
    def info(self, message: str):
        _logger.log(logging.INFO, message)
    
    def debug(self, message: str, data=None):
        if data is not None:
            if isinstance(data, dict):
                data = json.dumps(data, indent=4)
                message = f"{message}: {data}"
            else:
                data = MessageToDict(data)
                data = json.dumps(data, indent=4)
                message = f"{message}: {data}"

        _logger.log(logging.DEBUG, message)
    
    def error(self, message: str):
        _logger.log(logging.ERROR, message)

    def state(self, message: str):
        _logger.log(STATE, message)

    def record(self, message: str):
        _logger.log(RECORD, message)

    def event(self, data=None):
        _logger.log(EVENTS, json.dumps(data))

    def log(self, message: str, data=None, level=logging.INFO):
        if not (data is None):
            if isinstance(data, dict):
                data = json.dumps(data, indent=4)
                message = f"{message}: {data}"
            else:
                data = json.dumps(MessageToDict(data), indent=4)
                message = f"{message}: {data}"

        _logger.log(level, message)
    
    def flush(self):
        for handler in _logger.handlers:
            handler.flush()
