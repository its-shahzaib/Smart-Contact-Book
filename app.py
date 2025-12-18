# app.py - main Flask app with Login, CSV export, and CRUD
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_file
from flask_cors import CORS
from config import SECRET_KEY, DB_MODE
from models import init_db, fetch_all, fetch_one, execute
from utils import hash_password
import io
import csv
import os

app = Flask(__name__)
app.secret_key = SECRET_KEY
CORS(app)

# Initialize DB (creates tables)
init_db()

# Helper to adapt param style depending on DB mode
# For queries we use "?" for sqlite and "%s" for mysql. Simpler: write separate branches.
USE_SQLITE = (DB_MODE == 'sqlite')

def q_all(sql, params=()):
    if USE_SQLITE:
        # sqlite uses ? placeholders
        return fetch_all(sql.replace('%s','?'), params)
    else:
        return fetch_all(sql, params)

def q_one(sql, params=()):
    if USE_SQLITE:
        return fetch_one(sql.replace('%s','?'), params)
    else:
        return fetch_one(sql, params)

def q_exec(sql, params=()):
    if USE_SQLITE:
        return execute(sql.replace('%s','?'), params)
    else:
        return execute(sql, params)

# -----------------
# Authentication (very simple)
# -----------------
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    username = request.form.get('username','').strip()
    password = request.form.get('password','').strip()
    if not username or not password:
        return render_template('register.html', error='Username and password required')
    hashed = hash_password(password)
    try:
        if USE_SQLITE:
            q_exec("INSERT INTO users (username,password) VALUES (?,?)", (username, hashed))
        else:
            q_exec("INSERT INTO users (username,password) VALUES (%s,%s)", (username, hashed))
    except Exception as e:
        return render_template('register.html', error='User exists or DB error')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    username = request.form.get('username','').strip()
    password = request.form.get('password','').strip()
    if not username or not password:
        return render_template('login.html', error='Provide credentials')
    hashed = hash_password(password)
    if USE_SQLITE:
        user = q_one("SELECT * FROM users WHERE username=? AND password=?", (username, hashed))
    else:
        user = q_one("SELECT * FROM users WHERE username=%s AND password=%s", (username, hashed))
    if not user:
        return render_template('login.html', error='Invalid credentials')
    # store user id in session
    session['user_id'] = user['id']
    session['username'] = user['username']
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Decorator-like helper
def login_required(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return fn(*args, **kwargs)
    return wrapper

# -----------------
# Pages
# -----------------
@app.route('/')
@login_required
def home():
    return render_template('index.html')

@app.route('/edit/<int:cid>')
@login_required
def edit_page(cid):
    return render_template('edit.html', contact_id=cid)

# -----------------
# API endpoints (CRUD) - these operate on contacts for the logged in user
# -----------------
@app.route('/api/contacts', methods=['GET'])
@login_required
def api_get_contacts():
    user_id = session['user_id']
    if USE_SQLITE:
        rows = q_all("SELECT * FROM contacts WHERE user_id=?",(user_id,))
    else:
        rows = q_all("SELECT * FROM contacts WHERE user_id=%s",(user_id,))
    return jsonify(rows)

@app.route('/api/contacts', methods=['POST'])
@login_required
def api_add_contact():
    data = request.json
    name = data.get('name','').strip()
    phone = data.get('phone','').strip()
    email = data.get('email','').strip()
    if not name or not phone:
        return jsonify({'error':'Name and phone required'}), 400
    user_id = session['user_id']
    if USE_SQLITE:
        q_exec("INSERT INTO contacts (user_id,name,phone,email) VALUES (?,?,?,?)", (user_id,name,phone,email))
    else:
        q_exec("INSERT INTO contacts (user_id,name,phone,email) VALUES (%s,%s,%s,%s)", (user_id,name,phone,email))
    return jsonify({'ok':True})

@app.route('/api/contacts/<int:cid>', methods=['GET'])
@login_required
def api_get_contact(cid):
    user_id = session['user_id']
    if USE_SQLITE:
        row = q_one("SELECT * FROM contacts WHERE id=? AND user_id=?", (cid,user_id))
    else:
        row = q_one("SELECT * FROM contacts WHERE id=%s AND user_id=%s", (cid,user_id))
    if not row: return jsonify({'error':'Not found'}), 404
    return jsonify(row)

@app.route('/api/contacts/<int:cid>', methods=['PUT'])
@login_required
def api_update_contact(cid):
    user_id = session['user_id']
    data = request.json
    name = data.get('name','').strip()
    phone = data.get('phone','').strip()
    email = data.get('email','').strip()
    if not name or not phone:
        return jsonify({'error':'Name and phone required'}), 400
    if USE_SQLITE:
        q_exec("UPDATE contacts SET name=?, phone=?, email=? WHERE id=? AND user_id=?", (name,phone,email,cid,user_id))
    else:
        q_exec("UPDATE contacts SET name=%s, phone=%s, email=%s WHERE id=%s AND user_id=%s", (name,phone,email,cid,user_id))
    return jsonify({'ok':True})

@app.route('/api/contacts/<int:cid>', methods=['DELETE'])
@login_required
def api_delete_contact(cid):
    user_id = session['user_id']
    if USE_SQLITE:
        q_exec("DELETE FROM contacts WHERE id=? AND user_id=?", (cid,user_id))
    else:
        q_exec("DELETE FROM contacts WHERE id=%s AND user_id=%s", (cid,user_id))
    return jsonify({'ok':True})

# -----------------
# Export to CSV (only user's contacts)
# -----------------
@app.route('/export_csv')
@login_required
def export_csv():
    user_id = session['user_id']
    if USE_SQLITE:
        rows = q_all("SELECT * FROM contacts WHERE user_id=?",(user_id,))
    else:
        rows = q_all("SELECT * FROM contacts WHERE user_id=%s",(user_id,))
    # create CSV in-memory
    proxy = io.StringIO()
    writer = csv.writer(proxy)
    writer.writerow(['id','name','phone','email'])
    for r in rows:
        writer.writerow([r.get('id'), r.get('name'), r.get('phone'), r.get('email')])
    mem = io.BytesIO()
    mem.write(proxy.getvalue().encode('utf-8'))
    mem.seek(0)
    proxy.close()
    return send_file(mem,
                     as_attachment=True,
                     download_name='contacts.csv',
                     mimetype='text/csv')

# -----------------
# Run
# -----------------
if __name__ == '__main__':
    # ensure SQLite file exists when using sqlite
    if USE_SQLITE and not os.path.exists('contacts.db'):
        # models.init_db already called above
        pass
    app.run(debug=True)
