import os

file_path = 'app.py'
with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

# Replace index and serve_static
old_routes = """@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(FRONTEND_DIR, filename)"""

new_routes = """@app.route('/')
def index():
    return jsonify({"status": "ok", "message": "Placify API Backend is running."})"""

code = code.replace(old_routes, new_routes)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Removed static serving routes from app.py")
