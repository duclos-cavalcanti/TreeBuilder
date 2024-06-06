import time

class Timer():
    def __init__(self):
        pass

    def ts(self) -> int: 
        return int(time.time_ns() / 1_000)

    def future_ts(self, sec:float) -> int: 
        now = self.ts()
        return int(now + self.sec_to_usec(sec))

    def sleep_to(self, ts:int): 
        now = self.ts()
        if ts > now: 
            self.sleep_usec(ts - now)
        else:
            print(f"TRIGGER EXPIRED={ts} < NOW={now}")

    def sleep_sec(self, sec:float): 
        time.sleep(sec)

    def sleep_usec(self, usec:int): 
        print(f"SLEEP UNTIL: {usec}")
        self.sleep_sec(self.usec_to_sec(usec))
        print(f"AWAKE AT: {self.ts()}")

    def sec_to_usec(self, sec:float) -> float:
        return (sec * 1_000_000)
    
    def usec_to_sec(self, usec:int) -> float:
        return usec / 1_000_000

