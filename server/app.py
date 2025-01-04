from flask import Flask, request, jsonify
import subprocess
import tempfile
import os
import json

app = Flask(__name__)

@app.route('/api/run', methods=['POST'])
def run_code():
    # Get parameters from request
    data = request.get_json()
    code = data.get('code', '')
    problem = data.get('problem', '')
    language = data.get('language', 'python')

    if not code:
        return jsonify({"error": "No code provided"}), 400

    # Read test cases from file
    try:
        with open(f'problems/problems.json') as f:
            problem_data = json.load(f)
    except FileNotFoundError:
        return jsonify({"error": "Problem not found"}), 404

    problem_data = next((p for p in problem_data if p['id'] == problem), None)
    if not problem_data:
        return jsonify({"error": "Problem not found"}), 404
    test_cases = problem_data['test_cases']
    flag = problem_data['flag']

    # Define file extensions and commands for each language
    language_config = {
        'python': {'extension': '.py', 'command': ['python3']},
        'javascript': {'extension': '.js', 'command': ['node']},
        'java': {'extension': '.java', 'command': ['java']},
        'cpp': {'extension': '.cpp', 'command': ['g++', '-o', 'prog', 'prog.cpp']},
        'c': {'extension': '.c', 'command': ['gcc', '-o', 'prog', 'prog.c']}
    }

    if language not in language_config:
        return jsonify({"error": "Unsupported language"}), 400

    config = language_config[language]
    file_extension = config['extension']
    compile_command = config['command'] if language in ['c', 'cpp'] else None
    run_command = config['command'] if language not in ['c', 'cpp'] else ['./prog']

    results = []
    index = 1
    check = True

    for test in test_cases:
        if language in ['c', 'cpp']:
            with open(f'/tmp/prog{file_extension}', 'w') as temp_file:
                temp_file.write(code)
                temp_file_path = f'/tmp/prog{file_extension}'
        else:
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                temp_file.write(code.encode('utf-8'))
                temp_file_path = temp_file.name



        temp_dir = os.path.dirname(temp_file_path)
        executable_path = os.path.join(temp_dir, "prog")

        try:
            if compile_command:
                compile_process = subprocess.run(
                    compile_command,
                    cwd=temp_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                if compile_process.returncode != 0:
                    raise RuntimeError(f"Compilation error: {compile_process.stderr}")

            # Run the program
            process = subprocess.run(
                run_command + [temp_file_path] if language not in ['c', 'cpp'] else run_command,
                input=test['input'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5,
                universal_newlines=True,
                cwd=temp_dir
            )

            output = process.stdout.strip()

            if output == test['expected_output'].strip():
                if not test['hidden']:
                    results.append({"index": index, "input": test['input'], "output": output, "expected": test['expected_output'], "result": "Passed"})
                else:
                    results.append({"input": test['input'], "output": "hidden", "result": "Passed", "expected": "hidden"})           
            else:
                if not test['hidden']:
                    results.append({"index": index, "input": test['input'], "output": "Hidden", "expected": test['expected_output'], "result": "Failed"}) # Fix output
                else:
                    results.append({"input": test['input'], "result": "Failed", "message": f"Test case {index} failed"})
                check = False
                break

        except subprocess.TimeoutExpired:
            check = False
            results.append({"input": test['input'], "result": "Failed", "message": "Time limit exceeded"})
            break

        except Exception as e:
            check = False
            results.append({"input": test['input'], "result": "Failed", "message": str(e)})
            break

        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            if os.path.exists(executable_path) and language in ['c', 'cpp']:
                os.remove(executable_path)

        index += 1

    if check:
        return jsonify({"results": results, "flag": flag})
    else:
        return jsonify({"results": results})

if __name__ == '__main__':
    app.run(debug=False, port=5001)
