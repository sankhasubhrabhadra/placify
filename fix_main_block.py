import re

file_path = 'app.py'
with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

# Find the __main__ block
main_block = """if __name__ == '__main__':
    bootstrap_data()
    app.run(debug=True, port=5000)"""

if main_block in code:
    code = code.replace(main_block, "")
    # Add it to the end
    code = code.strip() + "\n\n" + main_block
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(code)
    print("Moved __main__ to the bottom")
else:
    print("Could not find exact main block")
