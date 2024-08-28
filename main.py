import numpy as np
import random
import networkx as nx
import matplotlib.pyplot as plt
import json
from utils.dependency import *
import time

# 获取当前时间戳
current_time = int(time.time())

# 使用时间戳作为种子
np.random.seed(current_time)

def read_items_from_json(filename):
    with open(filename, 'r') as f:
        return json.load(f)
    
items_flatten = read_items_from_json('data/items_flatten.json')
category = list(items_flatten.keys())


# Step 14: Generate English descriptions
# descriptions = []
# for key in G_d:
#     sentence = gen_sentence(G_d, key)
#     descriptions.append(sentence)


# parameter setting



# Example usage:
op_max = 10
ip_max = 8
G_d, Gnece_d, Topo = DrawAll(op_max, ip_max, items_flatten, category)

# TODO: 1. add sentence together 2. generate solution