import glob
import re

html_files = glob.glob('frontend/*.html')
js_files = glob.glob('frontend/*.js')

bad_override = """const originalFetch = window.fetch;
window.fetch = function() {
    let [resource, config] = arguments;
    if(config === undefined) {
        config = {};
    }
    config.credentials = 'include';
    return originalFetch(resource, config);
};"""

good_override = """const originalFetch = window.fetch;
window.fetch = function() {
    let [resource, config] = arguments;
    if(config === undefined) {
        config = {};
    }
    config.credentials = 'include';
    return originalFetch.call(window, resource, config);
};"""

for file_path in html_files + js_files:
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()
    
    if bad_override in code:
        code = code.replace(bad_override, good_override)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code)

print("Fixed Illegal Invocation error in fetch overrides")
