import re

file_path = 'app.py'
with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

# We will completely replace the end of interview_session_chat where it calls ask_groq
old_ask_block = r"""      # Ask Groq.*?return jsonify\(\{'success': True, 'response': response_text\}\)"""

new_ask_block = """      # Directly format messages for Ollama API to avoid role confusion
      ollama_messages = [{"role": "system", "content": final_prompt}]
      
      # Just append the actual message objects, ignoring the flattened history hack
      for m in messages:
          # Ensure roles map to what Ollama expects: 'user' or 'assistant'
          role = 'assistant' if m['role'] == 'assistant' else 'user'
          ollama_messages.append({"role": role, "content": m['content']})
          
      payload = {
          "model": os.environ.get('OLLAMA_MODEL', 'qwen2.5:1.5b'),
          "messages": ollama_messages,
          "stream": False,
          "options": {
              "temperature": 0.7
          }
      }
      
      try:
          response = requests.post("http://localhost:11434/api/chat", json=payload, timeout=60)
          response.raise_for_status()
          response_text = response.json()['message']['content'].strip()
          return jsonify({'success': True, 'response': response_text})
      except Exception as e:
          app.logger.error(f"Chat error: {e}")
          return jsonify({'success': False, 'error': 'AI service is temporarily unavailable.'}), 503"""

code = re.sub(old_ask_block, new_ask_block, code, flags=re.DOTALL)

# But wait, we still have `final_prompt += f"\n\nChat History:\n{history_text}"` above it. We need to remove the history_text injection.
history_injection = r"""      if history_text:\s+final_prompt \+= f"\\n\\nChat History:\\n\{history_text\}\""""
code = re.sub(history_injection, "", code)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Replaced ask_groq with direct Ollama call in interview_session_chat.")
