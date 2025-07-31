#Rohit gore
import random
import numpy as np


def author():
    return 'rgore32'


def study_group():
    return "rgore32"

if __name__ == "__main__":
    gtid = 903574004 #Rohit Gore gtid
    random.seed(gtid)
    np.random.seed(gtid)
    with open("experiment1.py") as e:
        exec(e.read())
    with open("experiment2.py") as f:
        exec(f.read())
    with open("ManualStrategy.py") as g:
        exec(g.read())

