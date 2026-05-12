from app.analysis.graph import analyze_dependencies

# Simulate 3 changed files
# payment.py and auth.py both import utils.py
# utils.py imports only os
changed_files = [
    {
        "filename": "app/payment.py",
        "content": """
import os
from app.utils import calculate
from app.models import Payment
"""
    },
    {
        "filename": "app/auth.py",
        "content": """
from app.utils import validate
from app.config import SECRET_KEY
"""
    },
    {
        "filename": "app/utils.py",
        "content": """
import os
import hashlib
"""
    },
]

graph, metrics = analyze_dependencies(changed_files)

print("=== GRAPH EDGES ===")
for edge in graph.edges():
    print(f"  {edge[0]}  →  {edge[1]}")

print("\n=== FILE METRICS ===")
for m in metrics:
    print(m)