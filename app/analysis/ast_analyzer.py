import ast
from typing import Optional


DECISION_NODES = (
    ast.If,        
    ast.For,       
    ast.While,     
    ast.ExceptHandler,  
    ast.With,      
    ast.Assert,    
    ast.BoolOp,    
)


def compute_cyclomatic_complexity(function_node: ast.FunctionDef) -> int:
    """
    Walk every node inside ONE function and count decision points.
    Cyclomatic complexity = number of decision points + 1
    
    The +1 represents the single straight-line path when there are no branches.
    """
    complexity = 1  

    for node in ast.walk(function_node):
        if isinstance(node, DECISION_NODES):
            complexity += 1

            if isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1

    return complexity


def compute_max_depth(tree: ast.AST) -> int:
    """
    Find the maximum nesting depth of function definitions in the file.
    
    A function defined inside another function adds one level of depth.
    We track this by passing the current depth as we recurse down the tree.
    """

    def _walk_depth(node: ast.AST, current_depth: int) -> int:
        """
        Recursive helper — walks the tree keeping track of depth.
        Returns the maximum depth found anywhere below this node.
        """
        max_found = current_depth  

        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                child_depth = _walk_depth(child, current_depth + 1)
            else:
                child_depth = _walk_depth(child, current_depth)

            max_found = max(max_found, child_depth)

        return max_found

    return _walk_depth(tree, 0)


def analyze_file(filename: str, file_content: str, lines_changed: int) -> Optional[dict]:
    """
    Main entry point — analyzes a single Python file.
    
    filename:      e.g. "app/payment.py"
    file_content:  the actual source code as a string
    lines_changed: additions + deletions (we get this from the GitHub diff)
    
    Returns a dict summary, or None if the file couldn't be parsed.
    """
    try:

        tree = ast.parse(file_content)

    except SyntaxError as e:
        print(f"[AST] Skipping {filename} — syntax error: {e}")
        return None


    functions = [
        node for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]

    if functions:
        complexities = [compute_cyclomatic_complexity(fn) for fn in functions]
        avg_complexity = sum(complexities) / len(complexities)
    else:
        avg_complexity = 0.0

    max_depth = compute_max_depth(tree)

    return {
        "filename":             filename,
        "cyclomatic_complexity": round(avg_complexity, 2),
        "max_function_depth":   max_depth,
        "lines_changed":        lines_changed,
        "function_count":       len(functions),
    }