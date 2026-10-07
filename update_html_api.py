import re
import glob

html_files = glob.glob('frontend/*.html')

for file_path in html_files:
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()
        
    # Inject API_BASE if not present
    if "<script>" in code and "const API_BASE" not in code:
        # Just replace the first <script> with <script> const API_BASE = '...';
        code = code.replace("<script>", f"<script>\\n      const API_BASE = 'https://coupon-casting-protocols-connection.trycloudflare.com';\\n", 1)
        
    code = re.sub(r"fetch\(['\"]/api/", "fetch(API_BASE + '/api/", code)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(code)

print("Updated HTML files to use direct API_BASE")
