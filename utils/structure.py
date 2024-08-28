import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

class Vertex:
    def __init__(self, name, layer):
        self.value = 0
        self.item_name = name
        self.layer = layer

def drawStructure(e, d, w0, w1, items_flatten, category):
    """
        d: number of layers (2, 3, 4)
        e: number of edges
        w: number of node per layer
    """
    l = np.full(d, w0)
    p = np.random.uniform(0,1)
    while not np.array_equal(l, np.full(d, w1)):
        e_minus = np.sum(l) - l[0]  # Minimum number of edges
        e_plus = sum(l[i] * l[i + 1] for i in range(len(l) - 1))  # Maximum number of edges

        if e_plus < e:
            i = np.random.choice([i for i in range(d) if l[i] < w1])
            l[i] += 1
        elif e_minus == e:
            break
        elif np.random.uniform(0,1) < p:
            i = np.random.choice([i for i in range(d) if l[i] < w1])
            l[i] += 1
        else:
            break
    
    # Construct the graph structure G_s with exactly l_i items on layer i
    Layers = dict[int, list[str]]() # {int(layer_i: listitem_names}

    adj_list = dict[Vertex, list[Vertex]]()
    num_edge = 0

    for i in range(d):
        names = np.random.choice(items_flatten[category[i]], l[i], replace=False)
        Layers[i] = [Vertex(name, i) for name in names]
    
        
    for i in range(d-1):
        for v in Layers[i]:
            index_b = np.random.choice(range(l[i+1]))
            b = Layers[i+1][index_b]
            adj_list[v] = [b]
            num_edge += 1

    
    # Adding more edges if the number of edges is less than e
    while num_edge < e:
        # Randomly select two layers to connect
        layer_a = np.random.choice(range(d - 1))
        layer_b = layer_a + 1
        
        # Randomly select vertices from adjacent layers
        a = np.random.choice(Layers[layer_a])
        b = np.random.choice(Layers[layer_b])
        
        # Add an edge if it doesn't exist
        if b not in adj_list[a]:
            adj_list[a].append(b)
            num_edge += 1
    
    # Return the structure
    return adj_list, Layers

def visualize_structure_graph(graph, layers, title="Structure Graph", filename=None):
    G = nx.DiGraph()
    
    # Add nodes to the graph
    for layer, nodes in layers.items():
        for node in nodes:
            G.add_node(node.item_name, layer=layer)
    
    # Add edges to the graph
    for node, neighbors in graph.items():
        for neighbor in neighbors:
            G.add_edge(node.item_name, neighbor.item_name)
    
    # Set up the plot
    plt.figure(figsize=(15, 10))
    plt.title(title)
    
    # Use a hierarchical layout
    pos = nx.multipartite_layout(G, subset_key="layer")
    
    # Draw the graph
    nx.draw(G, pos, with_labels=True, node_color='lightblue', 
            node_size=3000, font_size=8, font_weight='bold', 
            arrows=True, edge_color='gray')
    
    # Add labels to nodes
    labels = nx.get_node_attributes(G, 'label')
    nx.draw_networkx_labels(G, pos, labels, font_size=8)
    
    plt.axis('off')
    plt.tight_layout()
    
    if filename:
        plt.savefig(filename)
    else:
        plt.show()
    
    plt.close()