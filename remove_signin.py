import os
import glob
import re

frontend_dir = 'frontend'
html_files = glob.glob(os.path.join(frontend_dir, '*.html'))

for file_path in html_files:
    if os.path.basename(file_path) in ['login.html', 'signup.html']:
        continue
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Replace login.html links
    content = content.replace('href="login.html"', 'href="#"')
    content = content.replace("href='login.html'", 'href="#"')
    
    # Remove Logout button entirely
    # The logout button looks like:
    # <button class="icon-btn" onclick="handleLogout()" title="Logout">
    #   <i data-lucide="log-out"></i>
    # </button>
    logout_pattern = re.compile(r'<button[^>]*onclick="handleLogout\(\)"[^>]*>.*?<\/button>', re.DOTALL)
    content = re.sub(logout_pattern, '', content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

print("Removed all sign-in and logout buttons/links.")
