from app.analysis.scorer import compute_risk_score

# dummy data simulating outputs from AST analysis and graph metrics
ast_results = [
    {
        "filename":             "app/payment.py",
        "cyclomatic_complexity": 8.3,
        "max_function_depth":   4,
        "lines_changed":        120,
        "function_count":       5,
    },
    {
        "filename":             "app/utils.py",
        "cyclomatic_complexity": 3.1,
        "max_function_depth":   2,
        "lines_changed":        40,
        "function_count":       3,
    },
]

# dummy graph metrics for the changed files
graph_metrics = [
    {"filename": "app/payment.py", "in_degree": 6, "out_degree": 3, "dependent_count": 6},
    {"filename": "app/utils.py",   "in_degree": 9, "out_degree": 2, "dependent_count": 9},
]

result = compute_risk_score(ast_results, graph_metrics)

print("=== RISK SCORE RESULT ===")
for key, value in result.items():
    print(f"  {key:22} {value}")