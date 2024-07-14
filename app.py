from datetime import date
import os
from flask import Flask, flash, redirect, render_template, jsonify, request, url_for
from dotenv import load_dotenv
import google.generativeai as genai
import random
import sqlite3

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generate a random secret key

# Configure Gemini AI
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

def init_db():
    conn = sqlite3.connect('health_app.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS health_data
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT, weight TEXT, sleep TEXT, water TEXT, exercise TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS health_goals
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT, goal TEXT, target_date TEXT, status TEXT)''')
    conn.commit()
    conn.close()

# Initialize the database
init_db()

def get_db_connection():
    conn = sqlite3.connect('health_app.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/health_tracker', methods=['GET', 'POST'])
def health_tracker():
    if request.method == 'POST':
        conn = get_db_connection()
        conn.execute("INSERT INTO health_data (date, weight, sleep, water, exercise) VALUES (?, ?, ?, ?, ?)",
                     (request.form['date'], request.form['weight'], request.form['sleep'],
                      request.form['water'], request.form['exercise']))
        conn.commit()
        conn.close()
        flash('Health data saved successfully!', 'success')
        return redirect(url_for('health_tracker'))
    
    conn = get_db_connection()
    health_data = conn.execute("SELECT * FROM health_data ORDER BY date DESC").fetchall()
    conn.close()
    return render_template('health_tracker.html', health_data=health_data)

@app.route('/treatment_guidelines', methods=['GET', 'POST'])
def treatment_guidelines():
    guideline = ""
    if request.method == 'POST':
        condition = request.form['condition']
        prompt = f"Provide a brief treatment guideline for {condition}. Format the response with clear headings and bullet points. Keep it concise and general."
        response = model.generate_content(prompt)
        guideline = response.text
        
        # Convert bullet points to HTML lists
        guideline = guideline.replace('••', '<h3>')
        guideline = guideline.replace('•• ', '</h3><ul><li>')
        guideline = guideline.replace('• ', '</li><li>')
        guideline = guideline.replace('\n', '</li></ul>')
        
    return render_template('treatment_guidelines.html', guideline=guideline)

@app.route('/health_goals', methods=['GET', 'POST'])
def health_goals_route():
    if request.method == 'POST':
        conn = get_db_connection()
        conn.execute("INSERT INTO health_goals (date, goal, target_date, status) VALUES (?, ?, ?, ?)",
                     (date.today().strftime("%Y-%m-%d"), request.form['goal'],
                      request.form['target_date'], 'In Progress'))
        conn.commit()
        conn.close()
        flash('Health goal added successfully!', 'success')
        return redirect(url_for('health_goals_route'))
    
    conn = get_db_connection()
    health_goals = conn.execute("SELECT * FROM health_goals ORDER BY date DESC").fetchall()
    conn.close()
    return render_template('health_goals.html', health_goals=health_goals)

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

@app.route('/get_question', methods=['GET'])
def get_question():
    questions = [
        {"question": "How many glasses of water should you drink daily?", "answer": "8", "options": ["4", "6", "8", "10"]},
        {"question": "What vitamin is produced when your skin is exposed to sunlight?", "answer": "Vitamin D", "options": ["Vitamin A", "Vitamin C", "Vitamin D", "Vitamin E"]},
        {"question": "How many hours of sleep are recommended for adults?", "answer": "7-9", "options": ["5-6", "6-7", "7-9", "9-10"]},
        {"question": "Which of these is not a macronutrient?", "answer": "Vitamins", "options": ["Carbohydrates", "Proteins", "Fats", "Vitamins"]},
        {"question": "What is the normal resting heart rate for adults?", "answer": "60-100 bpm", "options": ["40-60 bpm", "60-100 bpm", "100-120 bpm", "120-140 bpm"]}
    ]
    question = random.choice(questions)
    return jsonify(question)

@app.route('/record')
def records():
    return render_template('records.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
