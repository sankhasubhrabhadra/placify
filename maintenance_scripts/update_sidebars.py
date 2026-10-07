import glob
import re

html_files = glob.glob('frontend/*.html')

new_link = """
        <a href="placement_session.html" class="nav-item">
          <i data-lucide="briefcase"></i>
          <span>Final Placement Prep</span>
        </a>"""

for file_path in html_files:
    if "placement_session.html" in file_path or "session_dashboard.html" in file_path:
        continue
        
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()
        
    if "placement_session.html" not in code:
        # We find the end of the Dashboard link block.
        # It looks like:
        # <a href="index.html" class="nav-item active">
        #   <i data-lucide="layout-dashboard"></i>
        #   <span>Dashboard</span>
        # </a>
        
        # We will use regex to find the closing </a> tag of the index.html link
        pattern = r'(<a href="index.html".*?</a>)'
        
        def replacement(match):
            return match.group(1) + new_link
            
        new_code = re.sub(pattern, replacement, code, flags=re.DOTALL)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_code)
            
print("Sidebar updated across all HTML files.")
