import re
import glob

html_files = glob.glob('frontend/*.html')

fetch_override = """
const originalFetch = window.fetch;
window.fetch = function() {
    let [resource, config] = arguments;
    if(config === undefined) {
        config = {};
    }
    config.credentials = 'include';
    return originalFetch(resource, config);
};
"""

for file_path in html_files:
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()
        
    if "const originalFetch = window.fetch;" not in code:
        # inject it right after API_BASE
        code = re.sub(r"(const API_BASE = 'https://playing-legitimate-suspended-unnecessary.trycloudflare.com';)", r"\1\n" + fetch_override, code)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code)

print("Updated HTML files with fetch credentials override")
