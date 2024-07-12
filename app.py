from datetime import date
import os
from flask import Flask, flash, redirect, render_template, jsonify, request, url_for
from dotenv import load_dotenv
import google.generativeai as genai

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generate a random secret key

# Load environment variables
load_dotenv()

# Configure Gemini AI
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

# Mock data storage (replace with a database in a real application)
health_data = []
health_goals = []  # Initialize as an empty list


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/health_tracker', methods=['GET', 'POST'])
def health_tracker():
    if request.method == 'POST':
        new_entry = {
            'date': request.form['date'],
            'weight': request.form['weight'],
            'sleep': request.form['sleep'],
            'water': request.form['water'],
            'exercise': request.form['exercise']
        }
        health_data.append(new_entry)
        flash('Health data saved successfully!', 'success')
        return redirect(url_for('health_tracker'))
    return render_template('health_tracker.html', health_data=health_data)

@app.route('/treatment_guidelines', methods=['GET', 'POST'])
def treatment_guidelines():
    guideline = ""
    if request.method == 'POST':
        condition = request.form['condition']
        prompt = f"Provide a brief treatment guideline for {condition}. Keep it concise and general."
        response = model.generate_content(prompt)
        guideline = response.text
    return render_template('treatment_guidelines.html', guideline=guideline)



# ... (keep other routes as they are)

@app.route('/health_goals', methods=['GET', 'POST'])
def health_goals_route():
    global health_goals
    if request.method == 'POST':
        new_goal = {
            'date': date.today().strftime("%Y-%m-%d"),
            'goal': request.form['goal'],
            'target_date': request.form['target_date'],
            'status': 'In Progress'
        }
        health_goals.append(new_goal)
        flash('Health goal added successfully!', 'success')
        return redirect(url_for('health_goals_route'))
    return render_template('health_goals.html', health_goals=health_goals)

# ... (keep other routes as they are)

@app.route('/health_game')
def health_game():
    questions = [
        {"question": "How many glasses of water should you drink daily?", "answer": "8", "options": ["4", "6", "8", "10"]},
        {"question": "What vitamin is produced when your skin is exposed to sunlight?", "answer": "Vitamin D", "options": ["Vitamin A", "Vitamin C", "Vitamin D", "Vitamin E"]},
        {"question": "How many hours of sleep are recommended for adults?", "answer": "7-9", "options": ["5-6", "6-7", "7-9", "9-10"]},
        {"question": "Which of these is not a macronutrient?", "answer": "Vitamins", "options": ["Carbohydrates", "Proteins", "Fats", "Vitamins"]},
        {"question": "What is the normal resting heart rate for adults?", "answer": "60-100 bpm", "options": ["40-60 bpm", "60-100 bpm", "100-120 bpm", "120-140 bpm"]}
    ]
    return render_template('health_game.html', questions=questions)

# If running the app directly with Gunicorn, the `__name__` will be `"__main__"`
if __name__ == '__main__':
    # For production, use Gunicorn to serve the app
    app.run(host='0.0.0.0', port=8000)