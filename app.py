from datetime import date
import os
from flask import Flask, flash, redirect, render_template, jsonify, request, url_for
from dotenv import load_dotenv
import google.generativeai as genai
from mailjet_rest import Client
import random

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generate a random secret key

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
        
        # Send confirmation email
        user_email = request.form['email']
        print(f"Attempting to send email to: {user_email}")
        try:
            send_confirmation_email(user_email, new_goal)
            flash('Health goal added successfully and confirmation email sent!', 'success')
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            flash('Health goal added successfully, but there was an error sending the confirmation email.', 'warning')
        
        return redirect(url_for('health_goals_route'))
    return render_template('health_goals.html', health_goals=health_goals)

def send_confirmation_email(to_email, goal):
    api_key = os.getenv('MAILJET_API_KEY')
    api_secret = os.getenv('MAILJET_API_SECRET')
    
    if not api_key or not api_secret:
        raise ValueError("Mailjet API key or secret is not set")

    mailjet = Client(auth=(api_key, api_secret), version='v3.1')
    data = {
      'Messages': [
        {
          "From": {
            "Email": "wafulasheila26@gmail.com",
            "Name": "Health Tracking App"
          },
          "To": [
            {
              "Email": to_email,
              "Name": "User"
            }
          ],
          "Subject": "New Health Goal Confirmation",
          "HTMLPart": f"""
            <p>Dear User,</p>
            <p>Your new health goal has been set successfully:</p>
            <p>Goal: {goal['goal']}</p>
            <p>Target Date: {goal['target_date']}</p>
            <p>Good luck on achieving your goal!</p>
            <p>Best regards,<br>Your Health Tracking App</p>
          """
        }
      ]
    }
    
    try:
        result = mailjet.send.create(data=data)
        if result.status_code == 200:
            print(f"Email sent successfully to {to_email}. Status code: {result.status_code}")
        else:
            print(f"Failed to send email. Status code: {result.status_code}")
            print(result.json())
    except Exception as e:
        print(f"Failed to send email. Error: {str(e)}")

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

# If running the app directly with Gunicorn, the `__name__` will be `"__main__"`
if __name__ == '__main__':
    # For production, use Gunicorn to serve the app
    app.run(host='0.0.0.0', port=8000)
