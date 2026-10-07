import glob
import re

TUNNEL_URL = "https://repair-pregnant-intelligent-configuring.trycloudflare.com"

# Update frontend/script.js directly
with open('frontend/script.js', 'r', encoding='utf-8') as f:
    script_js = f.read()

script_js = re.sub(r"const API_BASE = '.*?';", f"const API_BASE = '{TUNNEL_URL}';", script_js)

with open('frontend/script.js', 'w', encoding='utf-8') as f:
    f.write(script_js)

# Update HTML files inline scripts
html_files = glob.glob('frontend/*.html')
for file_path in html_files:
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()
    
    code = re.sub(r"const API_BASE = '.*?';", f"const API_BASE = '{TUNNEL_URL}';", code)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(code)

print(f"Updated all API_BASE references to {TUNNEL_URL}")
