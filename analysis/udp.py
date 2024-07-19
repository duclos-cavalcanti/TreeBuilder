import numpy as np
import csv

from typing import List

class UDP():
    def __init__(self):
        pass

    def read(self, f:str):
        data = []
        name = f.split("/")[-1]
        name = name.split(".csv")[0]

        with open(f, 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                data.append(int(row[1]))
        
        return data, name

    def process(self, files:List):
        for f in files: 
            data, name = self.read(f)
            data = np.array(data)
            p90     = np.percentile(data, 90)
            p75     = np.percentile(data, 75)
            p50     = np.percentile(data, 50)
            p25     = np.percentile(data, 25)
            std_dev = np.std(data)

            print(f"RESULTS[{name}]:")
            print(f"p90: {p90}")
            print(f"p75: {p75}")
            print(f"p50: {p50}")
            print(f"p25: {p25}")
            print(f"dev: {std_dev}")
            print()

