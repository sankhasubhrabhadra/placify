import glob

html_files = glob.glob('frontend/*.html')

for file_path in html_files:
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()
    
    # Check for literal \n
    if "\\n" in code:
        # replace cases where it's floating as a line
        code = code.replace("  \\n\n", "\n")
        code = code.replace("\\n\n", "\n")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code)

print("Fixed floating \\n in HTML files.")
