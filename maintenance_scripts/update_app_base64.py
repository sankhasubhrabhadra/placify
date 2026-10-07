import re

with open('app.py', 'r', encoding='utf-8') as f:
    app_code = f.read()

replacement = """@app.route('/api/resume/scan', methods=['POST'])
def scan_resume():
    try:
        file = None
        text = ''
        
        if request.is_json:
            data = request.get_json()
            text = data.get('text', '')
            base64_data = data.get('resume_base64')
            if base64_data:
                import tempfile, uuid, base64
                filename = data.get('filename', 'resume.pdf')
                temp_path = os.path.join(tempfile.gettempdir(), f'{uuid.uuid4()}_{filename}')
                with open(temp_path, 'wb') as f:
                    f.write(base64.b64decode(base64_data))
                try:
                    text = extract_text(temp_path)
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
        else:
            file = request.files.get('resume')
            text = request.form.get('text', '')
            if file:
                filename = secure_filename(file.filename)
                import tempfile, uuid
                temp_path = os.path.join(tempfile.gettempdir(), f'{uuid.uuid4()}_{filename}')
                file.save(temp_path)
                try:
                    text = extract_text(temp_path)
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)"""
                        
app_code = re.sub(r"@app.route\('/api/resume/scan', methods=\['POST'\]\)\ndef scan_resume\(\):\n    try:\n        file = request.files.get\('resume'\)\n        text = request.form.get\('text', ''\)\n        if file:\n            filename = secure_filename\(file.filename\)\n            import tempfile, uuid\n            temp_path = os.path.join\(tempfile.gettempdir\(\), f'\{uuid.uuid4\(\)}_\{filename\}'\)\n            file.save\(temp_path\)\n            try:\n                text = extract_text\(temp_path\)\n            finally:\n                if os.path.exists\(temp_path\):\n                    os.remove\(temp_path\)", replacement, app_code)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_code)

print("Updated app.py for Base64 resume uploads")
