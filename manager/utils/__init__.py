def format_addr( addr:str, diff:int=1000):
    split = addr.split(":")
    ip    = split[0]
    port  = int(split[1]) - diff
    return f"{ip}:{port}"
