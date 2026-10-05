from backend.engine import execute_code

# Test 1: Normal execution
code_normal = '''
def add(a, b):
    return a + b
'''
test_case_normal = {"input": {"a": 2, "b": 3}, "output": 5}

passed, output, error = execute_code(code_normal, test_case_normal)
print(f"Normal code passed: {passed}, output: {output}, error: {error}")

# Test 2: Network access attempt
code_malicious = '''
import urllib.request
def add(a, b):
    urllib.request.urlopen('http://example.com')
    return a + b
'''
test_case_malicious = {"input": {"a": 2, "b": 3}, "output": 5}

passed, output, error = execute_code(code_malicious, test_case_malicious)
print(f"Malicious code passed: {passed}, output: {output}, error: {error}")
