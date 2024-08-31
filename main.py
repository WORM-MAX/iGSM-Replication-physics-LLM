import numpy as np
import json
from utils.dependency import *
import time
from tqdm import tqdm

# 获取当前时间戳
current_time = int(time.time())

# 使用时间戳作为种子
np.random.seed(current_time)

def read_items_from_json(filename):
    with open(filename, 'r') as f:
        return json.load(f)
    
items_flatten = read_items_from_json('data_seed/items_flatten.json')
category = list(items_flatten.keys())

"""
    paramter:
        iGSM-med training: op_max = 15, ip_max = 20
        iGSM-med eval: force=True, op_max: 15,20-23, ip_max = 20
        iGSM-hard training: op_max = 21, ip_max = 28
        iGSM-hard eval: force=True, op_max: 21,28-32, ip_max = 28
"""


# Example usage:
op_max = 15
ip_max = 20

for _ in tqdm(range(100), desc="Generating graphs"):
    G_d, Gnece_d, Topo = DrawAll(op_max, ip_max, items_flatten, category)
