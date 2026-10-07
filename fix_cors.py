import re

# Update app.py
with open('app.py', 'r', encoding='utf-8') as f:
    app_code = f.read()

app_code = app_code.replace('CORS(app)', 'CORS(app, supports_credentials=True)')
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_code)

# Update frontend/script.js
with open('frontend/script.js', 'r', encoding='utf-8') as f:
    script_code = f.read()
    
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

if "const originalFetch = window.fetch;" not in script_code:
    # Inject it right after API_BASE
    script_code = re.sub(r"(const API_BASE = '.*?';)", r"\1\n" + fetch_override, script_code)
    with open('frontend/script.js', 'w', encoding='utf-8') as f:
        f.write(script_code)
        
print("Applied CORS credential overrides")
