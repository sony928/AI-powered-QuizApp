from flask import Flask, render_template, request
import google.generativeai as genai

app = Flask(__name__)

# Configure Gemini API Key (replace with your key or use env variables)
genai.configure(api_key="AIzaSyDxJAArLUsagkxu5hpMIEI2_3jo_5lasig")  # <-- Replace this!

# Initialize Gemini Model
model = genai.GenerativeModel('gemini-1.5-flash-latest')

def generate_mcqs(topic, difficulty, num_questions):
    # Prepare the prompt
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
        # Generate content from Gemini
        response = model.generate_content(prompt)
        mcqs_text = response.text.strip()  # Get the generated text
        return mcqs_text

    except Exception as e:
        return f"An error occurred: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    user_input = request.form['user_input']
    difficulty = request.form['difficulty']
    num_questions = request.form['num_questions']

    mcqs = generate_mcqs(user_input, difficulty, num_questions)

    return render_template('result.html', mcqs=mcqs)

if __name__ == '__main__':
    app.run(debug=True)
