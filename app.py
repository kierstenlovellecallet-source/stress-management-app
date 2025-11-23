# flask + stdlib imports
from flask import Flask, render_template, request, session, jsonify, make_response
import os
import sys

# When packaged with PyInstaller the application files are extracted to a
# temporary folder accessible via `sys._MEIPASS`. Use that as the base dir
# so Flask can find `templates/` and `static/` when built into a single exe.
base_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
app = Flask(__name__, template_folder=os.path.join(base_dir, 'templates'), static_folder=os.path.join(base_dir, 'static'))
# Use environment variable for secret in production
app.secret_key = os.environ.get('SECRET_KEY', 'change_me_in_prod')
# Optional access token to restrict public access. If set, requests must provide
# the token via `X-Access-Token` header, `access_token` query param, or a
# cookie named `access_token`.
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')


@app.before_request
def require_access_token():
    # If no token configured, allow all requests
    if not ACCESS_TOKEN:
        return None

    # Allow index and static assets to be requested without token so the
    # initial page can be loaded. If the index is opened with
    # `?access_token=...` the index route will set a cookie for subsequent
    # API requests (see `index()` below).
    if request.path == '/' or request.path.startswith('/static/') or request.path == '/favicon.ico':
        return None

    # Check header, query param, or cookie
    token = request.headers.get('X-Access-Token') or request.args.get('access_token') or request.cookies.get('access_token')
    if token != ACCESS_TOKEN:
        return jsonify({'error': 'Unauthorized'}), 401

# Questions for stress assessment
QUESTIONS = [
    "1. In the last month, how often have you been upset because of something that happened unexpectedly?",
    "2. In the last month, how often have you felt that you were unable to control the important things in your life?",
    "3. In the last month, how often have you felt nervous and 'stressed'?",
    "4. In the last month, how often have you felt confident about your ability to handle your personal problems?",
    "5. In the last month, how often have you felt that things were going your way?",
    "6. In the last month, how often have you found that you could not cope with all the things you had to do?",
    "7. In the last month, how often have you been able to control irritations in your life?",
    "8. In the last month, how often have you felt that you were on top of things?",
    "9. In the last month, how often have you been angered because of things that were outside of your control?",
    "10. In the last month, how often have you felt difficulties were piling up so high that you could not overcome them?"
]

# Reverse-scored question indices (0-based)
REVERSE_INDICES = [3, 4, 6, 7]

@app.route('/')
def index():
    # If an access_token query param is present, set it as a cookie so the
    # browser will include it for subsequent API requests.
    resp = make_response(render_template('index.html'))
    token = request.args.get('access_token')
    if token:
        resp.set_cookie('access_token', token, httponly=True)
    return resp

@app.route('/api/get-question', methods=['GET'])
def get_question():
    question_num = request.args.get('num', type=int, default=0)
    if question_num < len(QUESTIONS):
        return jsonify({'question': QUESTIONS[question_num], 'number': question_num + 1, 'total': len(QUESTIONS)})
    return jsonify({'error': 'No more questions'}), 404

@app.route('/api/submit-info', methods=['POST'])
def submit_info():
    data = request.json
    session['age'] = data.get('age')
    session['grade'] = data.get('grade')
    session['strand'] = data.get('strand')
    session['answers'] = []
    return jsonify({'success': True})

@app.route('/api/submit-answer', methods=['POST'])
def submit_answer():
    data = request.json
    answer = int(data.get('answer', -1))
    question_index = int(data.get('question_index', -1))
    
    if 'answers' not in session:
        session['answers'] = []
    
    session['answers'].append({'question': question_index, 'answer': answer})
    session.modified = True
    
    return jsonify({'success': True})

@app.route('/api/calculate-score', methods=['POST'])
def calculate_score():
    if 'answers' not in session:
        return jsonify({'error': 'No answers found'}), 400
    
    score = 0
    for item in session['answers']:
        question_index = item['question']
        value = item['answer']
        
        # Reverse scoring for specific questions
        if question_index in REVERSE_INDICES:
            value = 4 - value
        
        score += value
    
    # Determine stress level
    if score <= 13:
        stress_level = "Low Stress"
        advice = "You seem to be managing stress well. Keep up the good habits!"
    elif score <= 26:
        stress_level = "Moderate Stress"
        advice = "You're experiencing moderate stress. Consider taking breaks and practicing relaxation techniques."
    else:
        stress_level = "High Stress"
        advice = "You're experiencing high stress. Consider seeking support from a counselor or trusted person."
    
    return jsonify({
        'score': score,
        'stress_level': stress_level,
        'advice': advice,
        'age': session.get('age'),
        'grade': session.get('grade'),
        'strand': session.get('strand')
    })

if __name__ == '__main__':
    # Make host/port/debug configurable via environment variables so the
    # app can be exposed to other machines on the network (e.g. Chrome on
    # another computer or mobile device).
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() in ('1', 'true', 'yes')

    app.run(debug=debug, host=host, port=port)
