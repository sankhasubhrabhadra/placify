import os

file_path = os.path.join('backend', 'engine.py')
with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

old_start = """def execute_code(code_string: str, test_case: Dict[str, Any]) -> Tuple[bool, str, Any]:
    \"\"\"Execute Python code against a single test case.\"\"\"
    temp_file = None
    try:
        temp_file = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py", encoding="utf-8")
        temp_file.write(code_string)"""

new_start = """def execute_code(code_string: str, test_case: Dict[str, Any]) -> Tuple[bool, str, Any]:
    \"\"\"Execute Python code against a single test case.\"\"\"
    # NOTE: This is subprocess-level hardening, not full container isolation.
    # A hosted judge (Judge0, Piston) or Docker-based sandbox would be more robust for a real production deployment.
    temp_file = None
    try:
        temp_file = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py", encoding="utf-8")
        
        # Security: Prevent network access via Python audit hooks
        security_stub = (
            "import sys\\n"
            "def block_network(event, args):\\n"
            "    if event.startswith('socket.'):\\n"
            "        raise PermissionError('Network access is blocked in this sandbox')\\n"
            "sys.addaudithook(block_network)\\n\\n"
        )
        temp_file.write(security_stub)
        temp_file.write(code_string)"""

old_exec = "        result = subprocess.run([sys.executable, temp_file.name], capture_output=True, timeout=5, text=True)"

new_exec = """        # Security: Cap memory usage to 256MB on Linux
        kwargs = {}
        if sys.platform != 'win32':
            def set_limits():
                import resource
                mem_limit = 256 * 1024 * 1024
                resource.setrlimit(resource.RLIMIT_AS, (mem_limit, mem_limit))
            kwargs['preexec_fn'] = set_limits

        result = subprocess.run([sys.executable, temp_file.name], capture_output=True, timeout=5, text=True, **kwargs)"""

code = code.replace(old_start, new_start)
code = code.replace(old_exec, new_exec)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("backend/engine.py patched successfully.")
