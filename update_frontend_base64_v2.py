import re

with open('frontend/script.js', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace the formData construction and fetch call for /api/resume/scan
regex = re.compile(r"const formData = new FormData\(\);.*?body:\s*formData\s*\}\);", re.DOTALL)

new_fetch_block = """const file = fileInput && fileInput.files && fileInput.files[0];
      const textVal = pasteArea && pasteArea.value ? pasteArea.value.trim() : '';

      if (!file && !textVal) {
        resultsEl.innerHTML = '<div class="card">No resume provided. Upload a PDF or paste text.</div>';
        return;
      }

      let payload = { text: textVal };
      if (file) {
          payload.filename = file.name;
          // Convert file to base64
          const base64 = await new Promise((resolve, reject) => {
              const reader = new FileReader();
              reader.readAsDataURL(file);
              reader.onload = () => resolve(reader.result.split(',')[1]);
              reader.onerror = error => reject(error);
          });
          payload.resume_base64 = base64;
      }

      const response = await fetch(API_BASE + '/api/resume/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });"""

code, num_replacements = regex.subn(new_fetch_block, code)

with open('frontend/script.js', 'w', encoding='utf-8') as f:
    f.write(code)

print(f"Updated script.js to send Base64 JSON. Replacements made: {num_replacements}")
