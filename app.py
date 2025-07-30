
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'tajny_klucz'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS vehicles (id INTEGER PRIMARY KEY AUTOINCREMENT, make TEXT NOT NULL, model TEXT NOT NULL, image TEXT)")
    conn.commit()
    conn.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()
        if user:
            session['user'] = username
            return redirect(url_for('vehicle_list'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/')
def index():
    return redirect(url_for('vehicle_list'))

@app.route('/vehicles')
def vehicle_list():
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    vehicles = conn.execute('SELECT * FROM vehicles').fetchall()
    conn.close()
    return render_template('vehicle_list.html', vehicles=vehicles)

@app.route('/add-vehicle', methods=['GET', 'POST'])
def add_vehicle():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        make = request.form['make']
        model = request.form['model']
        file = request.files['image']
        filename = ''
        if file and file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        conn = get_db_connection()
        conn.execute('INSERT INTO vehicles (make, model, image) VALUES (?, ?, ?)', (make, model, filename))
        conn.commit()
        conn.close()
        return redirect(url_for('vehicle_list'))
    return render_template('add_vehicle.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
