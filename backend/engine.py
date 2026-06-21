"""
Assessment Engine Module

Handles coding question selection and Python code execution for assessments.
"""

import json
import os
import random
import subprocess
import sys
import tempfile
from typing import Any, Dict, List, Tuple

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "assessment"))
CODING_QUESTIONS_PATH = os.path.join(DATA_DIR, "questions.json")
HR_QUESTIONS_PATH = os.path.join(DATA_DIR, "hr_questions.json")


def select_hr_questions(n: int = 4) -> List[Dict]:
    """Select random HR interview questions."""
    questions = _load_json_data(HR_QUESTIONS_PATH)
    if not questions:
        return []
    n = min(n, len(questions))
    return random.sample(questions, n)


def _load_json_data(file_path: str) -> List:
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, encoding="utf-8") as handle:
            return json.load(handle)
    except (json.JSONDecodeError, OSError):
        return []


def select_coding_questions(job_role_id: int, score: int = None, n: int = None) -> List[Dict]:
    """Select coding questions based on resume score or admin configuration."""
    questions = _load_json_data(CODING_QUESTIONS_PATH)
    if not questions:
        return []

    n = n or 3
    level = "hard" if score and score >= 70 else "medium" if score and score >= 40 else "easy"
    pool = [q for q in questions if q.get("difficulty") == level] or questions

    chosen = random.sample(pool, min(n, len(pool)))
    random.shuffle(chosen)
    return chosen


def execute_code(code_string: str, test_case: Dict[str, Any]) -> Tuple[bool, str, Any]:
    """Execute Python code against a single test case."""
    temp_file = None
    try:
        temp_file = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py", encoding="utf-8")
        temp_file.write(code_string)
        temp_file.write("\n\n# AUTO-GENERATED TEST CODE\n")

        test_input = test_case.get("input", {})
        expected_output = test_case.get("output")

        if isinstance(test_input, dict):
            args_str = ", ".join([f"{k}={repr(v)}" for k, v in test_input.items()])
            func_name = next(
                (
                    line.split("(")[0].replace("def ", "").strip()
                    for line in code_string.split("\n")
                    if line.strip().startswith("def ")
                ),
                None,
            )

            if not func_name:
                return False, "", "Could not find function definition"

            test_code = (
                "import json\n"
                "try:\n"
                f"    result = {func_name}({args_str})\n"
                "    print(json.dumps(result, default=str))\n"
                "except Exception as e:\n"
                "    print(f'ERROR: {str(e)}')"
            )
        else:
            return False, "", "Invalid test case format"

        temp_file.write(test_code)
        temp_file.close()

        result = subprocess.run([sys.executable, temp_file.name], capture_output=True, timeout=5, text=True)
        output, error = result.stdout.strip(), result.stderr.strip() or None

        try:
            actual = json.loads(output) if output and not output.startswith("ERROR") else output
            passed = json.dumps(actual) == json.dumps(expected_output) or str(actual) == str(expected_output)
        except Exception:
            passed = output == str(expected_output)

        return passed, output, error
    except subprocess.TimeoutExpired:
        return False, "", "TIMEOUT: Code took too long (>5 seconds)"
    except Exception as exc:
        return False, "", f"Execution error: {str(exc)}"
    finally:
        if temp_file and os.path.exists(temp_file.name):
            try:
                os.remove(temp_file.name)
            except OSError:
                pass


def score_coding_answers(questions: List[Dict], answers: List[Dict]) -> Tuple[int, List[Dict]]:
    """Execute all solutions and return total score and detailed results."""
    results, total_score = [], 0
    for question in questions:
        answer = next((item for item in answers if item["id"] == question["id"]), None)
        if not answer:
            continue

        test_results, passed_count = [], 0
        for test_case in question.get("test_cases", []):
            passed, output, error = execute_code(answer["code"], test_case)
            if passed:
                passed_count += 1
            test_results.append({"passed": passed, "output": output, "error": error})

        question_score = (passed_count / len(question["test_cases"])) * 100 if question.get("test_cases") else 0
        total_score += question_score
        results.append({"question_id": question["id"], "score": question_score, "test_results": test_results})

    avg_score = total_score / len(questions) if questions else 0
    return int(avg_score), results
