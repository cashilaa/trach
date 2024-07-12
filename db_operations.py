import sqlite3
from datetime import date

def init_db():
    conn = sqlite3.connect('health_tracker.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS health_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            weight REAL,
            sleep REAL,
            water REAL,
            exercise TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS health_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            goal TEXT,
            target_date TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_health_data(entry):
    conn = sqlite3.connect('health_tracker.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO health_data (date, weight, sleep, water, exercise)
        VALUES (?, ?, ?, ?, ?)
    ''', (entry['date'], entry['weight'], entry['sleep'], entry['water'], entry['exercise']))
    conn.commit()
    conn.close()

def get_health_data():
    conn = sqlite3.connect('health_tracker.db')
    c = conn.cursor()
    c.execute('SELECT * FROM health_data')
    data = c.fetchall()
    conn.close()
    return data

def insert_health_goal(goal):
    conn = sqlite3.connect('health_tracker.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO health_goals (date, goal, target_date, status)
        VALUES (?, ?, ?, ?)
    ''', (goal['date'], goal['goal'], goal['target_date'], goal['status']))
    conn.commit()
    conn.close()

def get_health_goals():
    conn = sqlite3.connect('health_tracker.db')
    c = conn.cursor()
    c.execute('SELECT * FROM health_goals')
    goals = c.fetchall()
    conn.close()
    return goals
