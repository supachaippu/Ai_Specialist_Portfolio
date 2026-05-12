import os

def check_brackets(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    depth = 0
    stack = []
    for i, line in enumerate(lines):
        for char in line:
            if char == '{':
                depth += 1
                stack.append(i+1)
            elif char == '}':
                depth -= 1
                if stack: stack.pop()
                if depth < 0:
                    print(f"ERROR: Extra closing bracket at line {i+1}")
                    depth = 0
    
    if depth > 0:
        print(f"ERROR: {depth} unclosed brackets. Last opened at lines: {stack}")

check_brackets('index.html')
