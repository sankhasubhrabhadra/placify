import glob

TUNNEL_URL = "https://playing-legitimate-suspended-unnecessary.trycloudflare.com"

# 1. Update update_html_cors.py so we can reuse it
with open('update_html_cors.py', 'r', encoding='utf-8') as f:
    code = f.read()

import re
code = re.sub(r"const API_BASE = '.*?';", f"const API_BASE = '{TUNNEL_URL}';", code)

with open('update_html_cors.py', 'w', encoding='utf-8') as f:
    f.write(code)

# 2. Update frontend/script.js directly
with open('frontend/script.js', 'r', encoding='utf-8') as f:
    script_js = f.read()

script_js = re.sub(r"const API_BASE = '.*?';", f"const API_BASE = '{TUNNEL_URL}';", script_js)

with open('frontend/script.js', 'w', encoding='utf-8') as f:
    f.write(script_js)

# 3. Update frontend/vercel.json just in case
with open('frontend/vercel.json', 'r', encoding='utf-8') as f:
    vercel = f.read()

vercel = re.sub(r"https://.*?\.trycloudflare\.com", TUNNEL_URL, vercel)

with open('frontend/vercel.json', 'w', encoding='utf-8') as f:
    f.write(vercel)

# 4. Now run update_html_cors.py to update the inline script tags in all HTML files
import subprocess
subprocess.run(['python', 'update_html_cors.py'])

print(f"Updated all API_BASE references to {TUNNEL_URL}")
