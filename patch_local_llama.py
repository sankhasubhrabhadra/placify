import os

file_path = 'app.py'
with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

if "import requests" not in code:
    code = code.replace("import os", "import os\nimport requests")

old_ask_groq = """def ask_groq(system_prompt, user_message, model=None):
    if not GROQ_AVAILABLE or not GROQ_API_KEY or not groq_client:
        app.logger.error('Groq is not available or missing API key.')
        return None

    models_to_try = [model] if model else [GROQ_MODEL, GROQ_FALLBACK_MODEL]
    for m in models_to_try:
        try:
            completion = groq_client.chat.completions.create(
                model=m,
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user',   'content': user_message}
                ],
                max_tokens=512,
                temperature=0.7,
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            app.logger.error(f'Groq error with model {m}: {e}')
    
    return None"""

new_ask_groq = """def ask_groq(system_prompt, user_message, model=None):
    # Hijacked to use Local LLaMA via Ollama instead of Groq
    ollama_url = "http://localhost:11434/api/chat"
    model_name = os.environ.get('OLLAMA_MODEL', 'llama3.1') # Default to llama3.1
    
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "stream": False,
        "options": {
            "temperature": 0.7
        }
    }
    
    try:
        response = requests.post(ollama_url, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()['message']['content'].strip()
    except Exception as e:
        app.logger.error(f"Ollama local error: {e}")
        return None"""

code = code.replace(old_ask_groq, new_ask_groq)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated app.py to use Local Ollama")
