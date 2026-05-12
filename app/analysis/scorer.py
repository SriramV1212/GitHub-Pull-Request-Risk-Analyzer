MAX_COMPLEXITY = 20.0   # avg cyclomatic complexity across changed files
MAX_DEPENDENTS = 10.0   # avg dependent count across changed files
MAX_LINES      = 500.0  # total lines changed across all files

WEIGHT_COMPLEXITY = 0.40
WEIGHT_FANOUT     = 0.35
WEIGHT_LINES      = 0.25


def normalize(value: float, cap: float) -> float:
    """
    Converts a raw value to a 0.0–1.0 scale.
    
    value / cap gives the proportion.
    min(..., 1.0) ensures we never exceed 1.0 even if value > cap.
    max(..., 0.0) ensures we never go below 0.0.
    """
    return max(0.0, min(value / cap, 1.0))


def compute_risk_label(score: float) -> str:
    """
    Converts a numeric score to a human-readable label.
    
    0–30   → LOW
    31–60  → MEDIUM
    61–100 → HIGH
    """
    if score <= 30:
        return "LOW"
    elif score <= 60:
        return "MEDIUM"
    else:
        return "HIGH"


def compute_risk_score(
    ast_results:    list[dict],   # output from ast_analyzer.py
    graph_metrics:  list[dict],   # output from graph.py
) -> dict:
    """
    Master scoring function.
    
    Combines AST analysis and graph metrics into a single risk score.
    
    Returns a dict with:
        risk_score        — float, 0.0 to 100.0
        risk_label        — "LOW", "MEDIUM", or "HIGH"
        complexity_signal — normalized complexity, 0.0 to 1.0
        fanout_signal     — normalized fan-out, 0.0 to 1.0
        lines_signal      — normalized lines changed, 0.0 to 1.0
        files_analyzed    — how many files went into this score
    """

    if not ast_results:
        return {
            "risk_score":        0.0,
            "risk_label":        "LOW",
            "complexity_signal": 0.0,
            "fanout_signal":     0.0,
            "lines_signal":      0.0,
            "files_analyzed":    0,
        }

    # Average cyclomatic complexity across all changed files
    avg_complexity = sum(
        r["cyclomatic_complexity"] for r in ast_results
    ) / len(ast_results)

    complexity_signal = normalize(avg_complexity, MAX_COMPLEXITY)

    # Build a lookup: filename → dependent_count from graph metrics
    graph_lookup = {
        m["filename"]: m["dependent_count"]
        for m in graph_metrics
    }

    # Average dependent_count across all analyzed files
    # If a file has no graph entry, default to 0
    avg_dependents = sum(
        graph_lookup.get(r["filename"], 0) for r in ast_results
    ) / len(ast_results)

    fanout_signal = normalize(avg_dependents, MAX_DEPENDENTS)

    # Total lines changed across ALL files 
    total_lines = sum(r["lines_changed"] for r in ast_results)

    lines_signal = normalize(total_lines, MAX_LINES)

    raw_score = (
        complexity_signal * WEIGHT_COMPLEXITY +
        fanout_signal     * WEIGHT_FANOUT     +
        lines_signal      * WEIGHT_LINES
    )

    risk_score = round(raw_score * 100, 2)
    risk_label = compute_risk_label(risk_score)

    return {
        "risk_score":        risk_score,
        "risk_label":        risk_label,
        "complexity_signal": round(complexity_signal, 4),
        "fanout_signal":     round(fanout_signal,     4),
        "lines_signal":      round(lines_signal,      4),
        "files_analyzed":    len(ast_results),
    }