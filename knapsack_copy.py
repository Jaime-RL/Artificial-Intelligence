import collections

def read_knapsack_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
    
    # Find relevant lines
    capacity = None
    items = []
    
    for line in lines:
        line = line.strip()
        # Extract maximum weight capacity
        if line.startswith("MAXIMUM WEIGHT:"):
            capacity = int(line.split(":")[1].strip())
        # Extract item data (ID, value, weight)
        elif line and line[0].isdigit():
            parts = line.split()
            if len(parts) == 3:  # ID, value, weight
                item_id, value, weight = int(parts[0]), int(parts[1]), int(parts[2])
                items.append((item_id, weight, value))
    
    # Separate items into individual lists
    n = len(items)
    item_ids = [item[0] for item in items]
    weights = [item[1] for item in items]
    values = [item[2] for item in items]
    
    return capacity, n, weights, values, item_ids

# Read the file
capacity, n, weights, profits, item_ids = read_knapsack_file("knapsack.txt")
print(f"Capacity: {capacity}")
print(f"Items: {n}")
print(f"Weights: {weights}")
print(f"Profits: {profits}")
print(f"Item IDs: {item_ids}")



class Node:
    def __init__(self, level, profit, weight, choices):
        self.level = level
        self.profit = profit
        self.weight = weight
        self.choices = choices

    def gen_childs(self, weights, profits, capacity):
        childs = []
        new_level = self.level + 1
        
        # to prevent out of bonds
        if new_level <= len(weights):
            
            # CHILD WITH ITEM
            
            new_weight = self.weight + weights[self.level]
            
            if new_weight <= capacity:
                
                new_profit = self.profit + profits[self.level]
                new_choices = self.choices + [1]
                new = Node(new_level, new_profit, new_weight, new_choices)
                childs.append(new)
            
            # CHILD WITHOUT ITEM

            new_choices = self.choices + [0]
            childs.append(Node(new_level, self.profit, self.weight, new_choices))
        
        return childs
        

def BFS(capacity, n, weights, profits):
    
    # new queue
    fringe = collections.deque()
    root = Node(0, 0, 0, [])
    
    # variables
    best_profit = 0
    best_selection = []
    
    # add the root
    fringe.append(root)
    
    # while node that need to be explored
    while fringe:
        # pop the one to explore
        node_to_explore = fringe.pop()
        # if we have explored every node
        if node_to_explore.level == n:
            # we get the max profit
            if node_to_explore.profit > best_profit:
                best_profit = node_to_explore.profit
                best_selection = node_to_explore.choices
        # otherwise we keep exploring
        else:
            # gen the childs to explore
            childs = node_to_explore.gen_childs(weights, profits, capacity)
            # add those to the queue
            for child in childs:
                fringe.append(child)
    # solution
    return best_profit, best_selection
    

best_profit, best_selection = BFS(capacity, n, weights, profits)
print(f"Best Profit: {best_profit}")
print(f"Best selection: {best_selection}")



def DFS(capacity, n, weights, profits):

    # new 
    fringe = []
    root = Node(0, 0, 0, [])
    
    # variables
    best_profit = 0
    best_selection = []
    
    # add the root
    fringe.append(root)
    
    # while node that need to be explored
    while fringe:
        # pop the one to explore
        node_to_explore = fringe.pop()
        # if we have explored every node
        if node_to_explore.level == n:
            # we get the max profit
            if node_to_explore.profit > best_profit:
                best_profit = node_to_explore.profit
                best_selection = node_to_explore.choices
        # otherwise we keep exploring
        else:
            # gen the childs to explore
            childs = node_to_explore.gen_childs(weights, profits, capacity)
            # add those to the queue
            for child in childs:
                fringe.append(child)
        # solution
    return best_profit, best_selection
    

best_profit, best_selection = DFS(capacity, n, weights, profits)
print(f"Best Profit: {best_profit}")
print(f"Best selection: {best_selection}")