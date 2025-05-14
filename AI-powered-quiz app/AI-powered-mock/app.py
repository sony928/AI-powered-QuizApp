from flask import Flask, render_template, request, redirect, url_for, session
import google.generativeai as genai
import re
import json

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Required for session

# Configure Gemini API Key
genai.configure(api_key="AIzaSyDxJAArLUsagkxu5hpMIEI2_3jo_5lasig")

# Initialize Gemini Model
model = genai.GenerativeModel('gemini-1.5-flash-latest')

def parse_mcqs(mcqs_text):
    questions = []
    pattern = r'Q\d+: (.*?)\n\s*a\) (.*?)\n\s*b\) (.*?)\n\s*c\) (.*?)\n\s*d\) (.*?)\n\s*Answer: ([abcd])'
    matches = re.findall(pattern, mcqs_text, re.DOTALL)

    for match in matches:
        question_text, opt1, opt2, opt3, opt4, answer = match
        options = [opt1.strip(), opt2.strip(), opt3.strip(), opt4.strip()]
        answer_index = ['a', 'b', 'c', 'd'].index(answer.strip().lower())
        questions.append({
            'question': question_text.strip(),
            'options': options,
            'answer': answer_index
        })
    return questions

def generate_mcqs(topic, difficulty, num_questions):
    prompt = f"""
    Generate {num_questions} multiple choice questions on the topic "{topic}".
    The difficulty should be {difficulty}.
    Each question should have 4 options labeled a, b, c, d.
    Also, provide the correct answer after each question.

    Format:
    Q1: [question]
    a) option 1
    b) option 2
    c) option 3
    d) option 4
    Answer: [correct option letter]
    """

    try:
        response = model.generate_content(prompt)
        mcqs_text = response.text.strip()
        mcqs = parse_mcqs(mcqs_text)
        return mcqs
    except Exception as e:
        print("Error generating MCQs:", e)
        return []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    user_input = request.form['user_input']
    difficulty = request.form['difficulty']
    num_questions = int(request.form['num_questions'])

    mcqs = generate_mcqs(user_input, difficulty, num_questions)
    if not mcqs:
        return "Error generating MCQs. Please try again."

    session['mcqs'] = mcqs  # Store mcqs in session for review
    return render_template('exam.html', mcqs=json.dumps(mcqs), total_time=num_questions)

@app.route('/submit', methods=['POST'])
def submit():
    score = int(request.form['score'])
    total = int(request.form['total'])
    user_answers = json.loads(request.form['user_answers'])  # list of indices
    mcqs = json.loads(request.form['mcqs'])  # the quiz questions

    review_data = []
    for idx, q in enumerate(mcqs):
        user_ans_index = user_answers[idx] if user_answers[idx] is not None else -1
        correct_index = q['answer']
        review_data.append({
            'question': q['question'],
            'options': q['options'],
            'correct_answer': q['options'][correct_index],
            'user_answer': q['options'][user_ans_index] if user_ans_index >= 0 else "No Answer"
        })

    session['review'] = review_data
    return render_template('score.html', score=score, total=total)

@app.route('/review-attempt')
def review_attempt():
    review_data = session.get('review')
    if not review_data:
        return redirect(url_for('index'))
    return render_template('review-attempt.html', questions=review_data)

if __name__ == '__main__':
    app.run(debug=True)
