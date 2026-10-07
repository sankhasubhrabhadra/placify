import glob

html_files = glob.glob('frontend/*.html')

for file_path in html_files:
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()
    
    # Replace literal \n in the script tag
    code = code.replace(r"<script>\n", "<script>\n")
    code = code.replace(r"\n      const API_BASE", "\n      const API_BASE")
    # Actually just replace any literal \n that was incorrectly injected at the start of scripts
    code = code.replace("\\n      const API_BASE", "\n      const API_BASE")
    code = code.replace("<script>\\n", "<script>\n")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(code)

print("Removed literal \\n from HTML script tags")
