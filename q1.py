import itertools
import os

# --- Configuration ---
# Target directory
OUTPUT_DIR = r"C:\Users\idole\Documents\בר אילן\אימות פורמלי\Q1"

# Ensure directory exists
if not os.path.exists(OUTPUT_DIR):
    try:
        os.makedirs(OUTPUT_DIR)
        print(f"Created directory: {OUTPUT_DIR}")
    except OSError:
        OUTPUT_DIR = "."
        print("Warning: Could not create directory. Saving to current folder.")

# --- ROBDD Class ---
class ROBDD:
    def __init__(self, variables):
        self.vars = variables
        self.unique_table = {}
        # Node storage: 0=False, 1=True
        self.nodes = {0: (-1, None, None), 1: (-1, None, None)}
        self.node_counter = 2

    def _get_node(self, var_index, low, high):
        # Rule 1: Redundancy
        if low == high:
            return low
        # Rule 2: Uniqueness
        key = (var_index, low, high)
        if key in self.unique_table:
            return self.unique_table[key]

        node_id = self.node_counter
        self.nodes[node_id] = (var_index, low, high)
        self.unique_table[key] = node_id
        self.node_counter += 1
        return node_id

    def build(self, target):
        """
        Builds the BDD from a string formula or a python function.
        """
        return self._build_recursive(target, 0, {})

    def _build_recursive(self, target, var_idx, context):
        # Base case: All variables assigned
        if var_idx >= len(self.vars):
            try:
                # If target is a lambda function (for robust logic like Majority)
                if callable(target):
                    res = target(context)
                # If target is a string formula
                else:
                    res = eval(target, {"__builtins__": None}, context)
                return 1 if res else 0
            except Exception as e:
                print(f"Error during evaluation: {e}")
                return 0

        var_name = self.vars[var_idx]
        
        # Branch 0 (False)
        context[var_name] = False
        low = self._build_recursive(target, var_idx + 1, context)
        
        # Branch 1 (True)
        context[var_name] = True
        high = self._build_recursive(target, var_idx + 1, context)
        
        del context[var_name]
        return self._get_node(var_idx, low, high)

    def generate_dot_source(self, root_id):
        lines = []
        lines.append("digraph ROBDD {")
        lines.append("    rankdir=TB;")
        lines.append("    size=\"10\";")
        
        queue = [root_id]
        visited = set()
        
        while queue:
            node_id = queue.pop(0)
            if node_id in visited: continue
            visited.add(node_id)
            
            # Terminals styling
            if node_id == 0:
                lines.append(f'    {node_id} [label="0 (False)", shape=box, style=filled, fillcolor=lightpink, color=lightpink];')
                continue
            elif node_id == 1:
                lines.append(f'    {node_id} [label="1 (True)", shape=box, style=filled, fillcolor=lightgreen, color=lightgreen];')
                continue

            # Internal nodes styling
            var_idx, low, high = self.nodes[node_id]
            label = self.vars[var_idx]
            lines.append(f'    {node_id} [label="{label}", shape=ellipse, style=solid];')
            
            # Edges: 0=Red/Dashed, 1=Green/Solid
            lines.append(f'    {node_id} -> {low} [label="0", color=red, style=dashed, fontcolor=black];')
            lines.append(f'    {node_id} -> {high} [label="1", color=green, style=solid, fontcolor=black];')
            
            queue.append(low)
            queue.append(high)
            
        lines.append("}")
        return "\n".join(lines)

def save_graph_to_file(bdd_obj, root_id, filename_base):
    source_code = bdd_obj.generate_dot_source(root_id)
    full_path = os.path.join(OUTPUT_DIR, f"{filename_base}.txt")
    
    try:
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(source_code)
        # Explicit print for the user
        print(f"[V] Saved: {filename_base}.txt")
        print(f"    Path: {full_path}")
    except Exception as e:
        print(f"[X] Error saving {filename_base}: {e}")

# --- Helper for Q1c ---
def generate_greater_than_formula(x_vars, y_vars):
    if not x_vars or not y_vars: return "False"
    x_msb, y_msb = x_vars[0], y_vars[0]
    greater = f"({x_msb} and not {y_msb})"
    equal = f"(not ({x_msb} ^ {y_msb}))" 
    rest = generate_greater_than_formula(x_vars[1:], y_vars[1:])
    return f"({greater} or ({equal} and {rest}))"

# --- Main Execution ---

if __name__ == "__main__":
    print(f"--- Starting ROBDD Generation ---")
    print(f"Target Folder: {OUTPUT_DIR}\n")

    # === 1. Question 1a ===
    # Formula: (a and not c) or (b xor d)
    print("Processing Question 1a...")
    bdd_a = ROBDD(['a', 'b', 'c', 'd'])
    # logic: ((a and not c) or (b ^ d))
    root_a = bdd_a.build("((a and not c) or (b ^ d))")
    save_graph_to_file(bdd_a, root_a, "Assignment2_Q1a")
    print("")

    # === 2. Question 1b (Corrected Logic) ===
    print("Processing Question 1b (Majority)...")
    vars_b = ['x1', 'x2', 'x3', 'x4', 'x5']
    bdd_b = ROBDD(vars_b)
    # Using lambda for exact arithmetic logic (Sum >= 3)
    majority_func = lambda ctx: sum(ctx[v] for v in vars_b) >= 3
    root_b = bdd_b.build(majority_func)
    save_graph_to_file(bdd_b, root_b, "Assignment2_Q1b_Majority")
    print("")

    # === 3. Question 1c ===
    print("Processing Question 1c (X > Y)...")
    bdd_c = ROBDD(['x3', 'y3', 'x2', 'y2', 'x1', 'y1'])
    formula_c = generate_greater_than_formula(['x3', 'x2', 'x1'], ['y3', 'y2', 'y1'])
    root_c = bdd_c.build(formula_c)
    save_graph_to_file(bdd_c, root_c, "Assignment2_Q1c_GreaterThan")
    print("")

    # === 4. Extra Formula ===
    print("Processing Extra Formula (Parity)...")
    bdd_d = ROBDD(['x1', 'x2', 'x3', 'x4'])
    root_d = bdd_d.build("(not (x1 ^ x2 ^ x3 ^ x4))")
    save_graph_to_file(bdd_d, root_d, "Assignment3_Parity_check")
    print("\n--- Done! ---")