import os

file_path = 'frontend/style-additions.css'
modal_css = """
/* Modal Styles */
.modal-overlay {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0,0,0,0.8);
  z-index: 9999;
  justify-content: center;
  align-items: center;
  padding: 20px;
}
.modal-overlay.open {
  display: flex;
}
.modal-content {
  background: var(--surface);
  width: 100%;
  max-width: 500px;
  border-radius: var(--radius);
  border: 1px solid var(--border);
  padding: 24px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}
"""

with open(file_path, 'a', encoding='utf-8') as f:
    f.write(modal_css)

print("Modal CSS appended to style-additions.css")
