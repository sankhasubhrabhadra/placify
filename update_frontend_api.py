import re

TUNNEL_URL = "https://coupon-casting-protocols-connection.trycloudflare.com"

with open('frontend/script.js', 'r', encoding='utf-8') as f:
    code = f.read()

# Define API_BASE at the top
if "const API_BASE" not in code:
    code = f"const API_BASE = '{TUNNEL_URL}';\n" + code
else:
    # update existing API_BASE
    code = re.sub(r"const API_BASE = '.*?';", f"const API_BASE = '{TUNNEL_URL}';", code)

# Replace all fetch('/api/...) with fetch(API_BASE + '/api/...)
code = re.sub(r"fetch\(['\"]/api/", "fetch(API_BASE + '/api/", code)

# Note: We also need to fix any other places that might have hardcoded paths, but script.js only has fetch calls.
with open('frontend/script.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated script.js to use direct API_BASE")
