import string
import random
from utils.dependency import *

# Add this at the beginning of the file
MOD_VALUE = 23  # You can change this value as needed

def nodetoname(node, sentence=False):
    if node=="RNG":
        return node
    if isinstance(node[1], str):
        if sentence:
            return "each "+node[0].item_name+" 's "+node[1]
        else:
            return node[0].item_name+" 's "+node[1]
    else:
        if sentence:
            return "each "+node[0].item_name+" 's "+node[1].item_name
        else:
            return node[0].item_name + " 's " + node[1].item_name

def generate_var(G_value):
    new_var = None
    while new_var is None or new_var in G_value.values():
        new_var = random.choice(string.ascii_letters)
    return new_var


def generate_unnecessary_description(G_d, a):
    str_sentence = f"The number of {nodetoname(a, True)} equals"
    pool = [val for val in G_d[a]]
    if 'RNG' in pool:
        random_int = random.randint(0, MOD_VALUE - 1)
        str_sentence += f" {random_int}"
        pool.remove('RNG')
        if len(pool) > 0:
            plus_times = " + " if random.random() < 0.5 else " * "
            if plus_times == " + ":
                str_sentence += " more than"
            else:
                str_sentence += " times"

    if len(pool) == 1:
        b = nodetoname(pool[0], True)
        str_sentence += f" {b}"
    elif len(pool) == 2:
        b, c = nodetoname(pool[0], True), nodetoname(pool[1], True)
        sum_or_diff = " + " if random.random() < 0.5 else " - "
        if sum_or_diff == " + ":
            str_sentence += f" the sum of {b} and {c}"
        else:
            str_sentence += f" the difference of {b} and {c}"
    else:
        if pool:
            pool_name_list = []
            for i in pool:
                pool_name_list.append(nodetoname(i, True))
            random.shuffle(pool_name_list)
            str_sentence += " the sum of " + ", ".join(pool_name_list[:-1]) + f", and {pool_name_list[-1]}"

    return str_sentence




def gen_description(G_d, a, G_var, G_value):
    # Initialize the sentence string
    str_sentence = f"The number of {nodetoname(a, True)} equals"

    # Determine the pool of dependencies
    pool = [val for val in G_d[a]]

    var_a = G_var[a]
    solution = ["Define " + nodetoname(a, True) + " as " + var_a]

    num_step = ""

    # Check if RNG is in the pool
    if 'RNG' in pool:
        random_int = random.randint(0, MOD_VALUE - 1)
        str_sentence += f" {random_int}"
        pool.remove('RNG')
        if len(pool) > 0:
            plus_times = " + " if random.random() < 0.5 else " * "
            num_step = "So " + var_a + " = " + str(random_int) + plus_times
            if plus_times == " + ":
                str_sentence += " more than"
            else:
                str_sentence += " times"
        else:
            solution.append("So "+var_a+" = " + str(random_int))
            G_value[var_a] = random_int
            


    # Depending on the size of the pool, add to the sentence
    if len(pool) == 1:
        b = nodetoname(pool[0], True)
        str_sentence += f" {b}"
        var_1 = G_var[pool[0]]
        if not num_step:
            solution.append("So " + var_a + " = " + var_1 + " = " + str(G_value[var_1]))
            G_value[var_a] = G_value[var_1]
        else:
            if plus_times == " + ":
                G_value[var_a] = (G_value[var_1] + random_int) % MOD_VALUE
            else:
                G_value[var_a] = (G_value[var_1] * random_int) % MOD_VALUE
            num_step += var_1 + " = " + str(random_int) + plus_times + str(G_value[var_1]) + " = " + str(G_value[var_a])
            solution.append(num_step)
    elif len(pool) == 2:
        b, c = nodetoname(pool[0], True), nodetoname(pool[1], True)
        var_1 = G_var[pool[0]]
        var_2 = G_var[pool[1]]

        new_var = generate_var(G_value)

        sum_or_diff = " + " if random.random() < 0.5 else " - "
        if sum_or_diff == " + ":
            str_sentence += f" the sum of {b} and {c}"
            G_value[new_var] = (G_value[var_1] + G_value[var_2]) % MOD_VALUE
        else:
            str_sentence += f" the difference of {b} and {c}"
            G_value[new_var] = (G_value[var_1] - G_value[var_2]) % MOD_VALUE

        
        if not num_step:
            G_value[var_a] = G_value[new_var]
            solution.append("So " + var_a + " = " + var_1 + sum_or_diff + var_2 + " = " + str(G_value[var_1]) + sum_or_diff + str(G_value[var_2]) + " = " + str(G_value[var_a]))
        else:
            solution.append(new_var + " = " + var_1 + sum_or_diff + var_2 + " = " + str(G_value[var_1]) + sum_or_diff + str(G_value[var_2]) + " = " + str(G_value[new_var]))
            if plus_times == " + ":
                G_value[var_a] = (G_value[new_var] + random_int) % MOD_VALUE
            else:
                G_value[var_a] = (G_value[new_var] * random_int) % MOD_VALUE
            num_step += new_var + " = " + str(random_int) + plus_times + str(G_value[new_var]) + " = " + str(G_value[var_a])
            solution.append(num_step)
    else:
        if pool:
            pool_name_list = []
            pool_var_list = []
            for i in pool:
                pool_name_list.append(nodetoname(i, True))
                pool_var_list.append(G_var[i])
            while len(pool_var_list) > 2:
                new_var = generate_var(G_value)
                var_1 = pool_var_list[-1]
                var_2 = pool_var_list[-2]
                G_value[new_var] = (G_value[var_1] + G_value[var_2]) % MOD_VALUE
                solution.append(new_var + " = " + var_1 + " + " + var_2 + " = " + str(G_value[var_1]) + " + " + str(G_value[var_2]) + " = " + str(G_value[new_var]))
                pool_var_list.pop(-1)
                pool_var_list.pop(-1)
                pool_var_list.append(new_var)

            var_1 = pool_var_list[0]
            var_2 = pool_var_list[1]
            
            if not num_step:
                G_value[var_a] = (G_value[var_1] + G_value[var_2]) % MOD_VALUE
                solution.append("So " + var_a + " = " + var_1 + " + " + var_2 + " = " + str(G_value[var_1]) + " + " + str(G_value[var_2]) + " = " + str(G_value[var_a]))
            else:
                new_var = generate_var(G_value)
                G_value[new_var] = (G_value[var_1] + G_value[var_2]) % MOD_VALUE
                solution.append(new_var + " = " + var_1 + " + " + var_2 + " = " + str(G_value[var_1]) + " + " + str(G_value[var_2]) + " = " + str(G_value[new_var]))
                if plus_times == " + ":
                    G_value[var_a] = (G_value[new_var] + random_int) % MOD_VALUE
                else:
                    G_value[var_a] = (G_value[new_var] * random_int) % MOD_VALUE
                num_step += new_var + " = " + str(random_int) + plus_times + str(G_value[new_var]) + " = " + str(G_value[var_a])
                solution.append(num_step)

            random.shuffle(pool_name_list)
            str_sentence += " the sum of " + ", ".join(pool_name_list[:-1]) + f", and {pool_name_list[-1]}"

    return str_sentence, solution

def question_solution(G_d, Gnece_d, Topo, category,front=False):
    query = nodetoname(Topo[-1])
    a, b = query.split(" 's ")
    q = "How many " + b + " does " + a + " have?"

    # Generate English descriptions
    question_descriptions = []
    solution_descriptions = []

    # Create a list of available letters
    available_letters = list(string.ascii_letters)
    random.shuffle(available_letters)

    # Create the G_var dictionary
    G_var = {}
    for key in Gnece_d.keys():
        if available_letters:
            G_var[key] = available_letters.pop()
        else:
            # If we run out of letters, start combining them
            G_var[key] = ''.join(random.sample(string.ascii_letters, 2))

    G_value = dict[str, int]()

    for a in Topo:
        if not isinstance(a[1], str):
            sentence1, sentence2 = gen_description(Gnece_d, a, G_var, G_value)
            question_descriptions.append(sentence1)
            solution_descriptions.append(sentence2)
        else:
            index2 = category.index(a[1])
            index1 = a[0].layer

            var_a = G_var[a]
            solution_abs = ["Define " + nodetoname(a, True) + " as " + var_a]

            n = len(Gnece_d[a])
            if (index2-1)!=index1:
                # order: instance, abstract, instance
                
                assert(n%2==0)
                if n == 2:
                    var_1 = G_var[Gnece_d[a][0]]
                    var_2 = G_var[Gnece_d[a][1]]
                    G_value[var_a] = (G_value[var_1] * G_value[var_2]) % MOD_VALUE
                    solution_abs.append(var_a + " = " + var_1 + " * " + var_2 + " = " + str(G_value[var_1]) + " * " + str(G_value[var_2]) + " = " + str(G_value[var_a]))
                elif n > 2:
                    new_var_list = []
                    for i in range(n//2):
                        var_1 = G_var[Gnece_d[a][2*i]]
                        var_2 = G_var[Gnece_d[a][2*i+1]]
                        new_var = generate_var(G_value)
                        G_value[new_var] = (G_value[var_1] * G_value[var_2]) % MOD_VALUE
                        solution_abs.append(new_var + " = " + var_1 + " * " + var_2 + " = " + str(G_value[var_1]) + " * " + str(G_value[var_2]) + " = " + str(G_value[new_var]))
                        new_var_list.append(new_var)
                    while len(new_var_list) > 2:
                        new_var = generate_var(G_value)
                        var_1 = new_var_list[-1]
                        var_2 = new_var_list[-2]
                        G_value[new_var] = (G_value[var_1] + G_value[var_2]) % MOD_VALUE
                        solution_abs.append(new_var + " = " + var_1 + " + " + var_2 + " = " + str(G_value[var_1]) + " + " + str(G_value[var_2]) + " = " + str(G_value[new_var]))
                        new_var_list.pop(-1)
                        new_var_list.pop(-1)
                        new_var_list.append(new_var)
                    var_1 = new_var_list[0]
                    var_2 = new_var_list[1]
                    G_value[var_a] = (G_value[var_1] + G_value[var_2]) % MOD_VALUE
                    solution_abs.append("So " + var_a + " = " + var_1 + " + " + var_2 + " = " + str(G_value[var_1]) + " + " + str(G_value[var_2]) + " = " + str(G_value[var_a]))
            else:
                if n==1:
                    var_1 = G_var[Gnece_d[a][0]]
                    solution_abs.append("So " + var_a + " = " + var_1 + " = " + str(G_value[var_1]))
                    G_value[var_a] = G_value[var_1]
                elif n==2:
                    var_1 = G_var[Gnece_d[a][0]]
                    var_2 = G_var[Gnece_d[a][1]]
                    G_value[var_a] = (G_value[var_1] + G_value[var_2]) % MOD_VALUE
                    solution_abs.append("So " + var_a + " = " + var_1 + " + " + var_2 + " = " + str(G_value[var_1]) + " + " + str(G_value[var_2]) + " = " + str(G_value[var_a]))
                else:
                    new_var_list = []
                    for i in range(n):
                        new_var_list.append(G_var[Gnece_d[a][i]])
                    while len(new_var_list) > 2:
                        new_var = generate_var(G_value)
                        var_1 = new_var_list[-1]
                        var_2 = new_var_list[-2]
                        G_value[new_var] = (G_value[var_1] + G_value[var_2]) % MOD_VALUE
                        solution_abs.append(new_var + " = " + var_1 + " + " + var_2 + " = " + str(G_value[var_1]) + " + " + str(G_value[var_2]) + " = " + str(G_value[new_var]))
                        new_var_list.pop(-1)
                        new_var_list.pop(-1)
                        new_var_list.append(new_var)
                    var_1 = new_var_list[0]
                    var_2 = new_var_list[1]
                    G_value[var_a] = (G_value[var_1] + G_value[var_2]) % MOD_VALUE
                    solution_abs.append("So " + var_a + " = " + var_1 + " + " + var_2 + " = " + str(G_value[var_1]) + " + " + str(G_value[var_2]) + " = " + str(G_value[var_a]))
            
            solution_descriptions.append(solution_abs)


    for a_unne in [b for b in G_d if b not in Gnece_d]:
        if not isinstance(a_unne[1], str):
            question_descriptions.append(generate_unnecessary_description(G_d, a_unne))
        


        
    random.shuffle(question_descriptions)
    if not front:
        question =  ".\n".join(question_descriptions) + ".\n" + q
    else:
        question = q + ".\n" + ".\n".join(question_descriptions)

    solution = ""
    num_operation = 0
    for item in solution_descriptions:
        solution +=  "; ".join(item) + ".\n"
        num_operation += len(item) - 1
    return question, solution, num_operation

def structure_description(Layers, adj_list, category):
    structure_description = "Background: "
    for i in range(len(Layers)):
        structure_description += f"There are {len(Layers[i])} types of {category[i]}: " + ", ".join([item.item_name for item in Layers[i][:-1]]) + f", and {Layers[i][-1].item_name}.\n"
    for key, value in adj_list.items():
        if len(value) == 1:
            structure_description += f"Each {key.item_name} has {value[0].item_name}.\n"
        elif len(value) == 2:
            structure_description += f"Each {key.item_name} has {value[0].item_name} and {value[1].item_name}.\n"
        else:
            structure_description += f"Each {key.item_name} has " + ", ".join([item.item_name for item in value[:-1]]) + f", and {value[-1].item_name}.\n"
    
    return structure_description
