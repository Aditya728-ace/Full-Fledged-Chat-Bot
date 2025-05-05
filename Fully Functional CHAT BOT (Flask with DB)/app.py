from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import sqlite3
import google.generativeai as genai

app = Flask(__name__, template_folder='web', static_folder='web')
app.secret_key = 'your_secret_key' 

genai.configure(api_key='AIzaSyBlk-AzukxmjqorlZD-q18Jq-A-bfmeHqQ')    #Ye API key hai

def init_db():
    with sqlite3.connect('chat_history.db') as conn:
        cursor = conn.cursor()
        # Table for storing chat wali history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                user_message TEXT,
                bot_response TEXT
            )
        ''')
       
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT
            )
        ''')
        conn.commit()

init_db()  

@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password are required'})

    try:
        with sqlite3.connect('chat_history.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
        return jsonify({'success': True})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'Username already exists'})

@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/validate_login', methods=['POST'])
def validate_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    with sqlite3.connect('chat_history.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        record = cursor.fetchone()

    if record and record[0] == password:
        session['username'] = username 
        return jsonify({'success': True})

    return jsonify({'success': False})

@app.route('/chat')
def chat_page():
    if 'username' not in session:
        return redirect(url_for('login_page'))  
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    if 'username' not in session:
        return jsonify({'response': 'Error: Not logged in'})

    try:
        data = request.json
        user_input = data.get('user_input')
        username = session['username']

        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(user_input).text

        with sqlite3.connect('chat_history.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO history (username, user_message, bot_response)
                VALUES (?, ?, ?)
            ''', (username, user_input, response))
            conn.commit()

        return jsonify({'response': response})

    except Exception as e:
        return jsonify({'response': f"Error: {str(e)}"})

@app.route('/load_chat_history', methods=['GET'])
def load_chat_history():
    if 'username' not in session:
        return jsonify([])

    username = session['username']

    with sqlite3.connect('chat_history.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user_message, bot_response FROM history WHERE username = ?
        ''', (username,))
        messages = cursor.fetchall()  

    return jsonify(messages)

if __name__ == '__main__':
    app.run(debug=True, port=8080)
