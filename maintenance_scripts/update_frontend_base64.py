import re

with open('frontend/script.js', 'r', encoding='utf-8') as f:
    code = f.read()

old_fetch_block = """      const formData = new FormData();
      const file = fileInput && fileInput.files && fileInput.files[0];
      if (file) {
        formData.append('resume', file);
      } else if (pasteArea && pasteArea.value.trim()) {
        formData.append('text', pasteArea.value);
      }

      if (!file && (!pasteArea || !pasteArea.value.trim())) {
        resultsEl.innerHTML = '<div class="card">No resume provided. Upload a PDF or paste text.</div>';
        return;
      }

      try {
        const response = await fetch(API_BASE + '/api/resume/scan', {
          method: 'POST',
          body: formData
        });"""

new_fetch_block = """      const file = fileInput && fileInput.files && fileInput.files[0];
      const textVal = pasteArea ? pasteArea.value.trim() : '';

      if (!file && !textVal) {
        resultsEl.innerHTML = '<div class="card">No resume provided. Upload a PDF or paste text.</div>';
        return;
      }

      try {
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

code = code.replace(old_fetch_block, new_fetch_block)

with open('frontend/script.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated script.js to send Base64 JSON")
