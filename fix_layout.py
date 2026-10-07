import re
import glob

# Read the correct structure from jobs.html
with open('frontend/jobs.html', 'r', encoding='utf-8') as f:
    jobs_code = f.read()
    
# Extract everything from <body> to <main class="content-area"> (exclusive)
header_pattern = r'(<body>\s*<div class="layout-wrapper">.*?<main class="content-area">)'
header_match = re.search(header_pattern, jobs_code, flags=re.DOTALL)
if header_match:
    correct_header = header_match.group(1)
else:
    print("Failed to find header in jobs.html")
    exit(1)

# Now, we need to apply this header to placement_session.html and session_dashboard.html,
# while setting the correct "nav-item active" state for the sidebar in each.
def replace_header(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()
        
    old_header_pattern = r'<body>.*?(<main class="content-area">)'
    
    # We copy correct_header and change the active link
    my_header = correct_header.replace('class="nav-item active"', 'class="nav-item"')
    my_header = my_header.replace('<a href="placement_session.html" class="nav-item">', '<a href="placement_session.html" class="nav-item active">')
    
    new_code = re.sub(old_header_pattern, my_header + '\\n', code, flags=re.DOTALL)
    
    # Also need to make sure the closing tags match. 
    # Our generated files used `<div class="layout">` so there was an extra `</div>` at the end probably.
    # Actually, let's just make sure we end with `</main> </div> </div> </body> </html>`
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_code)
        
replace_header('frontend/placement_session.html')
replace_header('frontend/session_dashboard.html')

print("Fixed layout headers.")
