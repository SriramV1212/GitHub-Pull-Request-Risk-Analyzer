import ast
import networkx as nx
from typing import Optional


def extract_imports(file_content: str) -> list[str]:
    """
    Parse a Python file and return all imported module names.
    
    e.g. "import os" → ["os"]
         "from app.utils import helper" → ["app.utils"]
    """
    try:
        tree = ast.parse(file_content)
    except SyntaxError:
        return []

    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            # "import os, sys" → multiple aliases in one statement
            for alias in node.names:
                imports.append(alias.name)  

        elif isinstance(node, ast.ImportFrom):
            if node.module:   
                imports.append(node.module)  

    return imports


def build_dependency_graph(changed_files: list[dict]) -> nx.DiGraph:
    """
    Build a directed graph from a list of changed files.
    
    Each item in changed_files looks like:
    {
        "filename": "app/payment.py",
        "content": "import os\nfrom app.utils import helper\n..."
    }
    
    Returns a NetworkX DiGraph where:
    - Every file and its imports are nodes
    - Edge A → B means "file A imports module B"
    """
    graph = nx.DiGraph()   # directed graph — arrows have direction

    for file_info in changed_files:
        filename = file_info["filename"]
        content  = file_info["content"]


        graph.add_node(filename)

        imports = extract_imports(content)

        for imported_module in imports:
            graph.add_node(imported_module)

            # Add directed edge: this file → imported module
            # Meaning: this file DEPENDS ON the imported module
            graph.add_edge(filename, imported_module)

    return graph


def get_file_graph_metrics(
    graph: nx.DiGraph,
    changed_files: list[dict]
) -> list[dict]:
    """
    For each changed file, compute its graph metrics.
    
    in_degree       = number of files that import THIS file
                      (high = dangerous, many dependents)
    out_degree      = number of modules THIS file imports
                      (high = tightly coupled to many things)
    dependent_count = same as in_degree, named clearly for the scorer
    """
    metrics = []

    for file_info in changed_files:
        filename = file_info["filename"]

        # in_degree: how many arrows point INTO this node
        # = how many other files import this file
        in_deg = graph.in_degree(filename)

        # out_degree: how many arrows point OUT of this node
        # = how many modules this file imports
        out_deg = graph.out_degree(filename)

        metrics.append({
            "filename":        filename,
            "in_degree":       in_deg,
            "out_degree":      out_deg,
            "dependent_count": in_deg,   # alias — used by scorer
        })

    return metrics


def analyze_dependencies(changed_files: list[dict]) -> tuple[nx.DiGraph, list[dict]]:
    """
    Master function — builds the graph and returns metrics in one call.
    
    Returns:
        graph   — the full DiGraph (used for visualization later if needed)
        metrics — list of per-file dicts ready for the scorer
    """
    graph   = build_dependency_graph(changed_files)
    metrics = get_file_graph_metrics(graph, changed_files)
    return graph, metrics