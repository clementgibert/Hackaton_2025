from flask import Flask, render_template, request, redirect, session, url_for, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os

# 🔒 Charger les variables d'environnement depuis le fichier .env
load_dotenv()

app = Flask(__name__)

# 🔐 Clé secrète stockée dans .env ou fallback pour développement
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev_secret_key')

# ✅ Création automatique de la base si elle n'existe pas
def init_db():
    if not os.path.exists('users.db'):
        with sqlite3.connect('users.db') as conn:
            c = conn.cursor()
            c.execute('''
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            ''')
            conn.commit()
            print("📦 Base de données 'users.db' créée avec la table 'users'.")

init_db()

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        try:
            with sqlite3.connect('users.db') as conn:
                c = conn.cursor()
                c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
                conn.commit()
            flash("✅ Inscription réussie. Vous pouvez maintenant vous connecter.")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("⚠️ Nom d'utilisateur déjà utilisé.")
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect('users.db') as conn:
            c = conn.cursor()
            c.execute('SELECT password FROM users WHERE username = ?', (username,))
            result = c.fetchone()

            if result and check_password_hash(result[0], password):
                session['username'] = username
                return redirect(url_for('dashboard'))
            else:
                flash("❌ Identifiants incorrects.")
                return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'])

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
