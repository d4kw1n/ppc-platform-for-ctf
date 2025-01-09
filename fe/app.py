from flask import Flask, request, jsonify
from flask import render_template
import json
import requests

app = Flask(__name__)
URL = 'http://server:5001/api/run'

@app.route('/api/run', methods=['POST'])
def run_code():
    problem = request.args.get('problem', '')
    language = request.args.get('language', 'python')
    data = request.get_json()
    code = data.get('code', '')

    if not code:
        return jsonify({"error": "No code provided"}), 400
    
    payload = {
        'problem': problem,
        'language': request.args.get('language', language),
        'code': code
    }

    response = requests.post(URL, json=payload)
    print(response.json())

    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "Failed to execute code"}), response.status_code

@app.route('/')
def index():
    try:
        with open('problems/problems.json') as f:
            problems = json.load(f)
    except FileNotFoundError:
        return "Problem data not found", 404
    
    for problem in problems:
        if problem['public'] == False:
            problems.remove(problem)
            
    return render_template('index.html', problems=problems)

@app.route('/problems/<problem>')
def problem(problem):
    try:
        with open('problems/problems.json') as f:
            problem_data = json.load(f)
    except FileNotFoundError:
        return "Problem not found", 404

    problem_data = next((p for p in problem_data if p['id'] == problem), None)
    print(problem_data)
    if problem_data is None:
        return "Problem not found", 404
    testcase = problem_data['test_cases']
    testcase = [test for test in testcase if test['hidden'] == True]
    
    problem_data['test_cases'] = testcase
    
    return render_template('problem.html', problem=problem_data)

if __name__ == '__main__':
    app.run(debug=False, port=5000, host='0.0.0.0')
