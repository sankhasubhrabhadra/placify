import glob
import re
import json

TUNNEL_URL = "https://admit-allow-make-returns.trycloudflare.com"

# 1. Update frontend/script.js directly
with open('frontend/script.js', 'r', encoding='utf-8') as f:
    script_js = f.read()

script_js = re.sub(r"const API_BASE = '.*?';", f"const API_BASE = '{TUNNEL_URL}';", script_js)

with open('frontend/script.js', 'w', encoding='utf-8') as f:
    f.write(script_js)

# 2. Update HTML files inline scripts
html_files = glob.glob('frontend/*.html')
for file_path in html_files:
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()
    
    code = re.sub(r"const API_BASE = '.*?';", f"const API_BASE = '{TUNNEL_URL}';", code)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(code)

# 3. Update vercel.json
with open('frontend/vercel.json', 'r', encoding='utf-8') as f:
    vercel = f.read()

vercel = re.sub(r"https://.*?\.trycloudflare\.com", TUNNEL_URL, vercel)

with open('frontend/vercel.json', 'w', encoding='utf-8') as f:
    f.write(vercel)

print(f"Updated all API_BASE references and vercel rewrites to {TUNNEL_URL}")
