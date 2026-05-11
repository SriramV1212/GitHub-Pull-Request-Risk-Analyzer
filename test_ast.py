from app.analysis.ast_analyzer import analyze_file

sample_code = """
def calculate_discount(price, user_type, is_member):
    if user_type == "student":
        if is_member:
            return price * 0.5
        return price * 0.7
    elif user_type == "senior":
        return price * 0.6
    else:
        for discount in [0.1, 0.05]:
            if price > 100 and is_member:
                return price - discount
    return price

def simple_add(a, b):
    return a + b
"""

result = analyze_file(
    filename="app/pricing.py",
    file_content=sample_code,
    lines_changed=42
)

print(result)