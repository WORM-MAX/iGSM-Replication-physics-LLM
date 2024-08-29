import json

# Writing the items dictionary to a JSON file
def write_items_to_json(items, filename='items.json'):
    with open(filename, 'w') as f:
        json.dump(items, f, indent=4)

def read_items_from_json(filename='items.json'):
    with open(filename, 'r') as f:
        return json.load(f)


def flatten_list(nested_list):
    flat_list = []
    for item in nested_list:
        if isinstance(item, list):
            flat_list.extend(flatten_list(item))
        else:
            flat_list.append(item)
    return flat_list

loded_items = read_items_from_json()

category = ["District", "Supermarkets", "Product", "Ingredient"]

items_flatten = dict()
for i in range(4):
    items_flatten[category[i]] = flatten_list(list(loded_items[category[i]].values()))

write_items_to_json(items_flatten, 'items_flatten.json')

write_items_to_json(loded_items)

# "each " + "'s "