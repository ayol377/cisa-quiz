import random
from flask import Flask, render_template, request, redirect, url_for
import json

app = Flask(__name__)

# Load the JSON data
with open('quiz-data.json') as f:
    data = json.load(f)

# Constants
QUESTIONS_PER_QUIZ = 20  # Set constant for number of questions

# Initialize the quiz state
def init_quiz():
    global current_question, correct_answers, questions
    # Make sure we don't try to sample more questions than we have
    num_questions = min(QUESTIONS_PER_QUIZ, len(data['questions']))
    question_indexes = random.sample(range(len(data['questions'])), num_questions)
    questions = [data['questions'][i] for i in question_indexes]
    current_question = 0
    correct_answers = 0

# Initialize on startup
init_quiz()

@app.route('/', methods=['GET', 'POST'])
def quiz():
    global current_question, correct_answers, questions
    
    try:
        if request.method == 'POST':
            # Get the user's answer
            user_answer = request.form.get('answer')
            
            # Validate that we have a current question
            if current_question >= len(questions):
                return redirect(url_for('quiz', reset=True))
                
            # Check if answer was provided
            if not user_answer:
                return render_template('quiz.html',
                                    error="Please select an answer",
                                    question=questions[current_question]['questionText'],
                                    options=questions[current_question]['options'],
                                    current_question=current_question + 1,
                                    total_questions=len(questions))
            
            # Check if the answer is correct
            is_correct = user_answer == questions[current_question]['correctAnswer']
            if is_correct:
                correct_answers += 1
            
            # Render the explanation page
            return render_template('explanation.html',
                                question=questions[current_question]['questionText'],
                                options=questions[current_question]['options'],
                                is_correct=is_correct,
                                user_answer=user_answer,
                                correct_answer=questions[current_question]['correctAnswer'],
                                explanation=questions[current_question]['explanation'],
                                current_question=current_question + 1,
                                total_questions=len(questions))
                                
        elif request.method == 'GET' and 'continue' in request.args:
            # Increment the question index
            current_question += 1
            
            # Check if there are more questions
            if current_question < len(questions):
                # Render the next question
                return render_template('quiz.html',
                                    question=questions[current_question]['questionText'],
                                    options=questions[current_question]['options'],
                                    current_question=current_question + 1,
                                    total_questions=len(questions))
            else:
                # No more questions, render the final result
                p = (correct_answers / len(questions))
                p = max(200, int(p * 800))
                return render_template('result.html',
                                    total_questions=len(questions),
                                    correct_answers=correct_answers)
                                    
        elif request.method == 'GET' and 'reset' in request.args:
            # Reset the quiz state
            init_quiz()
            return redirect(url_for('quiz'))
            
        else:
            # Render the first question
            return render_template('quiz.html',
                                question=questions[current_question]['questionText'],
                                options=questions[current_question]['options'],
                                current_question=current_question + 1,
                                total_questions=len(questions))
                                
    except Exception as e:
        # Handle any errors gracefully
        print(f"Error in quiz route: {str(e)}")
        init_quiz()  # Reset the quiz state
        return redirect(url_for('quiz'))

if __name__ == '__main__':
    app.run(debug=True)