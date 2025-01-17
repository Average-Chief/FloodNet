from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from functools import wraps
from flask import request, Response

def check_auth(username, password):
    return username == 'loki' and password == 'yoursaviorishere'

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return Response(
                'Login required', 401,
                {'WWW-Authenticate': 'Basic realm="Login Required"'}
            )
        return f(*args, **kwargs)
    return decorated

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']

    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (name, email, phone) VALUES (?, ?, ?)', (name, email, phone))
        conn.commit()
        conn.close()
        return redirect(url_for('success'))
    except sqlite3.IntegrityError:
        return "Email already registered. Please try again with a different email."

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/admin/users')
@requires_auth
def admin_users():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall() 

    conn.close()
    return render_template('admin_user.html', users=users)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
