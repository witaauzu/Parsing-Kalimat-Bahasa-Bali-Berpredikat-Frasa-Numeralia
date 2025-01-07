from itertools import combinations

def get_terminals(grammar):
    """Extract all terminal symbols from the grammar."""
    terminals = set()
    for productions in grammar.values():
        for production in productions:
            for symbol in production:
                if symbol not in grammar:
                    terminals.add(symbol)
    return terminals

def remove_epsilon_productions(cfg):
    """Remove epsilon productions from the grammar."""
    nullable = set()
    
    # Find nullable symbols
    changed = True
    while changed:
        changed = False
        for head, bodies in cfg.items():
            if head not in nullable:
                for body in bodies:
                    if len(body) == 0 or all(symbol in nullable for symbol in body):
                        nullable.add(head)
                        changed = True
                        break
    
    # Generate new rules
    new_cfg = {}
    for head, bodies in cfg.items():
        new_bodies = set()
        for body in bodies:
            if body:  # Skip empty productions
                indices = [i for i, symbol in enumerate(body) if symbol in nullable]
                for r in range(len(indices) + 1):
                    for subset in combinations(indices, r):
                        new_body = tuple(sym for i, sym in enumerate(body) if i not in subset)
                        if new_body:  # Only add non-empty productions
                            new_bodies.add(new_body)
        new_cfg[head] = [list(body) for body in new_bodies]
    return new_cfg

def remove_unit_productions(cfg):
    """Remove unit productions from the grammar."""
    # Get all unit pairs
    unit_pairs = set()
    for head, bodies in cfg.items():
        for body in bodies:
            if len(body) == 1 and body[0] in cfg:
                unit_pairs.add((head, body[0]))
    
    # Add transitive unit pairs
    changed = True
    while changed:
        changed = False
        for a, b in list(unit_pairs):
            for c in [p[1] for p in unit_pairs if p[0] == b]:
                if (a, c) not in unit_pairs:
                    unit_pairs.add((a, c))
                    changed = True
    
    # Create new grammar
    new_cfg = {head: [] for head in cfg}
    for head, bodies in cfg.items():
        # Add non-unit productions
        for body in bodies:
            if len(body) != 1 or (len(body) == 1 and body[0] not in cfg):
                new_cfg[head].append(body)
        
        # Add productions from unit pairs
        for pair in unit_pairs:
            if pair[0] == head:
                for body in cfg[pair[1]]:
                    if len(body) != 1 or (len(body) == 1 and body[0] not in cfg):
                        if body not in new_cfg[head]:
                            new_cfg[head].append(body)
    return new_cfg

def convert_to_cnf(cfg):
    """Convert grammar to Chomsky Normal Form."""
    # Step 1: Create new grammar with terminals replaced
    new_cfg = {}
    terminal_rules = {}
    counter = 0
    
    # First, create rules for terminals
    for head, bodies in cfg.items():
        new_cfg[head] = []
        for body in bodies:
            new_body = []
            for symbol in body:
                if symbol not in cfg and len(body) > 1:
                    terminal_name = f"T{symbol}"
                    if terminal_name not in terminal_rules:
                        terminal_rules[terminal_name] = [[symbol]]
                    new_body.append(terminal_name)
                else:
                    new_body.append(symbol)
            new_cfg[head].append(new_body)
    
    # Add terminal rules to grammar
    new_cfg.update(terminal_rules)
    
    # Step 2: Convert long productions
    final_cfg = {}
    for head in new_cfg:
        final_cfg[head] = []
    
    for head, bodies in new_cfg.items():
        for body in bodies:
            if len(body) <= 2:
                final_cfg[head].append(body)
            else:
                # Create new rules for long productions
                current_head = head
                remaining_body = body[:]
                while len(remaining_body) > 2:
                    new_head = f"X{counter}"
                    counter += 1
                    final_cfg[current_head].append([remaining_body[0], new_head])
                    if new_head not in final_cfg:
                        final_cfg[new_head] = []
                    current_head = new_head
                    remaining_body = remaining_body[1:]
                final_cfg[current_head].append(remaining_body)
    
    return final_cfg