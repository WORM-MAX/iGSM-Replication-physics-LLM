import random
import os
import datetime
from utils.structure import *
from utils.description import *
import json

def add_graphs(graph1, graph2):
    # 创建一个新字典来存储合并后的图
    if graph1 is None:
        return graph2
    if graph2 is None:
        return graph1
    combined_graph = {}

    # 合并第一个图的所有节点及其邻居
    for node, neighbors in graph1.items():
        if node not in combined_graph:
            combined_graph[node] = []
        combined_graph[node].extend(neighbors)

    # 合并第二个图的所有节点及其邻居
    for node, neighbors in graph2.items():
        if node not in combined_graph:
            combined_graph[node] = []
        combined_graph[node].extend(neighbors)

    # 去重处理：确保每个节点的邻居列表中没有重复项
    for node in combined_graph:
        combined_graph[node] = list(set(combined_graph[node]))

    return combined_graph

def operation(G):
    num = 0
    for node, dependency in G.items():
        num += max(len(dependency)-1, 1)
    return num



def find_depend(abs_para, adj_list, G, category):
    index2 = category.index(abs_para[1])
    index1 = abs_para[0].layer
    #print(index1, index2)
    if (index2-1)==index1:
        G[abs_para] = []
        for item in adj_list[abs_para[0]]:
            instance_para = (abs_para[0], item)
            G[instance_para] = []
            G[abs_para].append(instance_para)
    else:
        G[abs_para] = []
        for item in adj_list[abs_para[0]]:
            instance_para = (abs_para[0], item)
            G[instance_para] = []
            G[abs_para].append(instance_para)
            abs_para_middle = (item, abs_para[1])
            G[abs_para].append(abs_para_middle)
            find_depend(abs_para_middle, adj_list, G, category)
    return G




def drawNecessary1(Layers, adj_list, n, m, category):
    Gnece1 = dict[tuple, list]()
    updated = True
    d = len(Layers)
    abs_candidates = dict[int, list[tuple]]()
    while updated: 
        updated = False
        for i in range(d - 1, 0, -1):
            if i in abs_candidates:
                candidates = abs_candidates[i]
            else:
                abs_candidates[i] = []
                for j in range(d-i):
                    for item in Layers[j]:
                        abs_candidates[i].append((item, category[i+j]))
                candidates = abs_candidates[i]
                
            candidates = [param for param in candidates if param not in Gnece1]
            if candidates:
                index = np.random.choice(len(candidates))
                selected_param = candidates[index]
                #print('try')
                G = dict()
                G1 = find_depend(selected_param, adj_list, G, category)
                #print(len(G1))

                G_prime = add_graphs(Gnece1, G1)

                if operation(G_prime) <= n:
                    Gnece1 = G_prime
                    updated = True
                    break

    Gnece2 = Gnece1

     # Add more instance parameters to Gnece2_d
    all_instance_para = [] 
    for key, value in adj_list.items():
        for v in value:
            all_instance_para.append((key, v))
    
    left_instance_para = [para for para in all_instance_para if para not in Gnece1]
    # Calculate how many more instance parameters we need to add
    num_to_add = m - operation(Gnece2)

    # Randomly choose num_to_add instance parameters (or all remaining if there are fewer)
    num_to_add = min(num_to_add, len(left_instance_para))
    selected_indices = np.random.choice(len(left_instance_para), num_to_add, replace=False)

    for index in selected_indices:
        selected_instance_para = left_instance_para[index]
        Gnece2[selected_instance_para] = []
    
    return Gnece2




def draw_necessary2(Gnece2_d):
    """
    Constructs Gnece3_d and a random topological ordering Topo as per D.2.2.
    """
    Gnece3_d = Gnece2_d
    Topo = []

    def next1(Topo, G_topo):
        # necessary torwards the computation of query
        return [a for a in G_topo if any(a in Gnece3_d[b] for b in Topo)]

    def next2(Topo, G_topo):
        # if not, some other parameter depends on it and is not yet added to Topo
        #dependent_params = set(b for a in G_topo for b in Gnece3_d[a])
        #return list(set(G_topo) - dependent_params)
        return [a for a in G_topo if not any(a in Gnece3_d[b] for b in G_topo if b != a)]
        #return [a for a in G_topo if not any(a in Gnece3_d[b] for b in G_topo if b != a)]

    def biased_random_selection(param_set):
        if not param_set:
            return None
        
        # Convert param_set to a list if it's not already
        param_set = param_set
        
        # Generate a random Gaussian value
        g = np.random.normal(0, 1)

        def weight(a):
            # Define weight function as per the remark
            return (isinstance(a[1], str) + (a in next1(Topo, G_topo))) * abs(g)
        
        # Calculate the weights for each parameter in the set
        weights = [weight(a) for a in param_set]

        # Convert weights to probabilities
        probabilities = np.exp(weights)
        probabilities /= probabilities.sum()

        # Sample a parameter according to the calculated probabilities
        index = np.random.choice(len(param_set), p=probabilities)
        selected_param = param_set[index]
        
        return selected_param


    while True:
        G_topo = [a for a in Gnece3_d if a not in Topo]
        if not Topo:
            param0 = random.choice(next2(Topo, G_topo))
            #print(next2(Topo, G_topo))
        else:
            possible = list(set(next1(Topo, G_topo)).intersection(set(next2(Topo, G_topo)))) # intersection: rid some of intermediate abstract para
            param0 = random.choice(possible)
        
        Topo.insert(0, param0)
        # for para in Topo:
        #     print(nodetoname(para))
        # print('end')
        G_topo = [a for a in Gnece3_d if a not in Topo]
        if not G_topo:
            break
        if not list(set(next1(Topo, G_topo)).intersection(set(next2(Topo, G_topo)))):
            if isinstance(param0[1], str):
                return (None, None)
            param1 = biased_random_selection(next2(Topo, G_topo))
            if param1 is not None:
                Gnece3_d[param0].append(param1)
        elif not isinstance(param0[1], str):
            # Probability event p0
            p0 = np.random.uniform(0, 1)
            p1 = np.random.uniform(0, 1)
            if p1 < p0:
                param1 = biased_random_selection(G_topo)
                if param1 is not None:
                    Gnece3_d[param0].append(param1)

    return Gnece3_d, Topo




def draw_necessary3(Gnece3_d, Topo, s):
    cur_op = dict[tuple, int]()
    for a in Gnece3_d:
        cur_op[a] = max(1, len(Gnece3_d[a])-1)

    def max_op(a, Topo):
        return min(3, max(1, Topo.index(a)))
    
    while sum(cur_op.values()) < s:
        eligible = []
        for a in Gnece3_d:
            if (not isinstance(a[1], str)) and cur_op[a] < max_op(a, Topo):
                eligible.append(a)
        if not eligible:
            return None
        a = random.choice(eligible)
        cur_op[a] += 1

    G_d_nece = {k: list(v) for k, v in Gnece3_d.items()}
    
    G_d_nece["RNG"] = []
    for a in Gnece3_d:
        if not isinstance(a[1], str):
            pool = ["RNG"] + Topo[:Topo.index(a)]
            if cur_op[a] == 1:
                dep_num = random.choice([1, 2])
            else:
                dep_num = cur_op[a] + 1
            dep_num = min(dep_num, len(pool))
            re = [b for b in Gnece3_d[a] if b in pool]
            for r in re:
                pool.remove(r)
                dep_num -= 1
            if dep_num == len(pool):
                G_d_nece[a].extend(pool)
            else:
                if np.random.uniform(0,1)>0.5:
                    G_d_nece[a].append("RNG")
                    dep_num -= 1
                pool.remove("RNG")
                if dep_num > 0:
                    indexs = np.random.choice(len(pool), dep_num, replace=False)
                    for index in indexs:
                        G_d_nece[a].append(pool[index])

    return G_d_nece





def draw_unnecessary(adj_list, Layers, G_d_nece, category):
    # 创建一个新的图结构来存储修改后的图
    G_d_nece_copy = {k: list(v) for k, v in G_d_nece.items()}
    
    # Initialize the graph G_d and the IndList
    IndList = []

    all_instance_para = [] 
    for key, value in adj_list.items():
        for v in value:
            all_instance_para.append((key, v))

    def check_depend(abs_para):
        index2 = category.index(abs_para[1])
        index1 = abs_para[0].layer
        depend_list = []
        #print(index1, index2)
        for item in adj_list[abs_para[0]]:
            instance_para = (abs_para[0], item)
            if instance_para not in G_d_nece_copy:
                return False
            else:
                depend_list.append(instance_para)
            if (index2-1)!=index1:
                abs_para_middle = (item, abs_para[1])
                if abs_para_middle not in G_d_nece_copy:
                    return False
                else:
                    depend_list.append(abs_para_middle)
                    sub_depend_list = check_depend(abs_para_middle)
                if not sub_depend_list:
                    return False
                else:
                    depend_list.extend(sub_depend_list)
        return depend_list

    def abs_com_G():
        abs_computable = []
        # sample abs para
        d = len(Layers)
        for i in range(d - 1, 0, -1):
            for j in range(d-i):
                for item in Layers[j]:
                    abs_para = (item, category[i+j])
                    if abs_para not in G_d_nece_copy and check_depend(abs_para):
                        abs_computable.append(abs_para)
        return abs_computable
                        

    # Main loop
    while any(param not in G_d_nece_copy for param in all_instance_para):
        # Step 3: Combine all parameters in G_d and computable parameters
        K = set(G_d_nece_copy.keys())
        K.update(abs_com_G())

        # Randomly select an instance parameter a from G_s that is not in G_d
        a = random.choice([param for param in all_instance_para if param not in G_d_nece_copy])
        G_d_nece_copy[a] = []  # Add a to G_d

        # Randomly decide the pool
        if random.random() < 0.5:
            pool = set(IndList + ['RNG'])
            IndList.append(a)
        else:
            pool = K.union(['RNG'])

        # Initialize dep_num
        dep_num = 1

        # While loop for dependency count
        while dep_num < min(4, len(pool)):
            if random.random() < 0.5:
                dep_num += 1
            else:
                break

        # Determine the selected set
        if dep_num == len(pool):
            selected = pool
        else:
            selected = set()
            if random.random() < 0.5:
                selected.add('RNG')
                dep_num -= 1
            pool.discard('RNG')
            selected.update(random.sample(list(pool), dep_num))

        # Add selected dependencies to G_d
        for b in selected:
            G_d_nece_copy[a].append(b)
            if b not in G_d_nece_copy:
                if isinstance(b[1], str):
                    G_d_nece_copy[b] = check_depend(b)
                else:
                    G_d_nece_copy[b] = []


    return G_d_nece_copy



def visualize_dependency_graph(graph, title="Dependency Graph", filename=None):
    G = nx.DiGraph()

    # Add all nodes to the graph, including isolated ones
    for node in graph.keys():
        G.add_node(nodetoname(node))
    
    # Add edges to the graph and store edge colors
    edge_colors = []
    for node, neighbors in graph.items():
        for neighbor in neighbors:
            G.add_edge(nodetoname(node), nodetoname(neighbor))
            # Add your condition here to determine if the edge should be red
            if isinstance(node[1], str):
                edge_colors.append('red')
            else:
                edge_colors.append('gray')
    
    # Set up the plot
    plt.figure(figsize=(12, 8))
    plt.title(title)
    
    # Use a spring layout
    pos = nx.spring_layout(G, k=0.9, iterations=50)
    
    # Draw the graph with colored edges
    nx.draw(G, pos, with_labels=True, node_color='lightblue', 
            node_size=2000, font_size=8, font_weight='bold', 
            arrows=True, edge_color=edge_colors)
    
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



def create_unique_folder(base_path):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    folder_name = f"draw_all_log_{timestamp}"
    path = os.path.join(base_path, folder_name)
    
    if not os.path.exists(path):
        os.makedirs(path)
        return path
    
    index = 1
    while True:
        new_path = f"{path}_{index}"
        if not os.path.exists(new_path):
            os.makedirs(new_path)
            return new_path
        index += 1
import json
import datetime

def DrawAll(op_max, ip_max, items_flatten, category, force=False):
    # 创建一个唯一的日志文件夹
    log_folder = create_unique_folder("log")

    log_file = os.path.join(log_folder, "log.txt")

    # Function to write to the log file
    def write_log(message):
        with open(log_file, "a") as f:
            f.write(message + "\n")

    # Step 1-2: Determine s
    t0, t1 = np.random.randint(1, op_max + 1, size=2)
    s = min(t0, t1)
    if force:
        s = op_max
    write_log(f"s: {s}")

    # Step 3-4: Determine n and m
    t0, t1 = np.random.randint(1, s + 1, size=2)
    n = max(t0, t1)
    m = np.random.randint(n, s + 1)
    write_log(f"n: {n}")
    write_log(f"m: {m}")

    # Step 5: Determine d
    rel = (s - 1) / (ip_max - 1)
    weight = [-(rel - 0.2)**2, -(rel - 0.5)**2, -(rel - 0.8)**2]
    probs = np.exp(weight) / np.sum(np.exp(weight))  # softmax
    d = np.random.choice([2, 3, 4], p=probs)
    write_log(f"d: {d}")

    # Step 6-7: Determine w0 and w1
    t0, t1 = np.random.choice([2, 3, 4], size=2, p=probs)
    w0, w1 = min(t0, t1), max(t0, t1)
    write_log(f"w0: {w0}")
    write_log(f"w1: {w1}")

    # Step 8: Determine e
    t0, t1 = np.random.randint((d - 1) * w0, ip_max + 1, size=2)
    e = min(t0, t1, (d - 1) * w1**2)
    write_log(f"e: {e}")

    # Step 9: Draw Structure
    adj_list, Layers = drawStructure(e, d, w0, w1, items_flatten, category)
    structure_file = os.path.join(log_folder, "structure_graph.png")
    visualize_structure_graph(adj_list, Layers, filename=structure_file)
    write_log(f"Structure graph saved to: {structure_file}")

    # Step 10: Draw Necessary1
    Gnece2_d = drawNecessary1(Layers, adj_list, n, m, category)
    necessary1_file = os.path.join(log_folder, "necessary1_graph.png")
    visualize_dependency_graph(Gnece2_d, title="Necessary1 Graph", filename=necessary1_file)
    write_log(f"Necessary1 graph saved to: {necessary1_file}")

    # Step 11: Draw Necessary2
    for _ in range(1000):
        Gnece3_d, Topo = draw_necessary2(Gnece2_d)
        if Gnece3_d is not None:
            necessary2_file = os.path.join(log_folder, "necessary2_graph.png")
            visualize_dependency_graph(Gnece3_d, title="Necessary2 Graph", filename=necessary2_file)
            write_log(f"Necessary2 graph saved to: {necessary2_file}")
            
            # Log Topo
            write_log("Topological order:")
            for node in Topo:
                write_log(f"  {nodetoname(node)}")
            
            break
    else:
        write_log("Retrying DrawAll due to failure in draw_necessary2")
        return DrawAll(op_max, ip_max, items_flatten, category, force)  # Retry from the beginning

    # Step 12: Draw Necessary3
    Gnece_d = draw_necessary3(Gnece3_d, Topo, s)
    if Gnece_d is None:
        write_log("Retrying DrawAll due to failure in draw_necessary3")
        return DrawAll(op_max, ip_max, items_flatten, category, force)  # Retry from the beginning
    else:
        necessary3_file = os.path.join(log_folder, "necessary3_graph.png")
        visualize_dependency_graph(Gnece_d, title="Necessary3 Graph", filename=necessary3_file)
        write_log(f"Necessary3 graph saved to: {necessary3_file}")
        
    # Step 13: Draw Unnecessary
    G_d = draw_unnecessary(adj_list, Layers, Gnece_d, category)
    unnecessary_file = os.path.join(log_folder, "unnecessary_graph.png")
    visualize_dependency_graph(G_d, title="Unnecessary Graph", filename=unnecessary_file)
    write_log(f"Unnecessary graph saved to: {unnecessary_file}")
    structure_des = structure_description(Layers, category)
    question, solution, num_operation = question_solution(G_d, Gnece_d, Topo, category)
    # Write question and solution to log
    write_log("\nQuestion:")
    write_log(structure_des + question)
    write_log("\nSolution:")
    write_log(solution)
    assert(num_operation==s)

    write_log("DrawAll completed successfully")

    # Create a dictionary to store all logged terms
    logged_terms = {
        "s": int(s),
        "n": int(n),
        "m": int(m),
        "d": int(d),
        "w0": int(w0),
        "w1": int(w1),
        "e": int(e),
        "structure_graph": structure_file,
        "necessary1_graph": necessary1_file,
        "necessary2_graph": necessary2_file,
        "topological_order": [nodetoname(node) for node in Topo],
        "necessary3_graph": necessary3_file,
        "unnecessary_graph": unnecessary_file,
        "question": structure_des + question,
        "solution": solution,
        "num_operation": num_operation
    }

    # Create the dataset folder if it doesn't exist
    dataset_folder = "dataset"
    os.makedirs(dataset_folder, exist_ok=True)

    # Generate a unique filename for the JSON file
    json_filename = f"logged_terms_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.json"
    json_filepath = os.path.join(dataset_folder, json_filename)

    # Save the logged terms to the JSON file
    with open(json_filepath, 'w') as json_file:
        json.dump(logged_terms, json_file, indent=2)

    write_log(f"Logged terms saved to: {json_filepath}")

    return G_d, Gnece_d, Topo
    return G_d, Gnece_d, Topo


