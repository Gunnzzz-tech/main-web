from flask import Flask, render_template, request, redirect, url_for, flash
import os
import sqlite3
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Upload folder
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database setup
DB_PATH = 'job_portal.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS applicants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            email TEXT,
            phone TEXT,
            country TEXT,
            city TEXT,
            address TEXT,
            position TEXT,
            additional_info TEXT,
            resume_path TEXT,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- Routes ---

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/apply', methods=['GET', 'POST'])
def apply():
    if request.method == 'GET':
        role = request.args.get('role', '')
        return render_template('index.html', selected_role=role)

    elif request.method == 'POST':
        try:
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            country = request.form.get('country')
            city = request.form.get('city')
            address = request.form.get('address')
            position = request.form.get('position')
            additional_info = request.form.get('additional_info')

            file = request.files.get('resume')
            resume_path = None
            if file and file.filename:
                filename = secure_filename(file.filename)
                resume_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(resume_path)

            # Save to DB
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('''
                INSERT INTO applicants 
                (first_name, last_name, email, phone, country, city, address, position, additional_info, resume_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (first_name, last_name, email, phone, country, city, address, position, additional_info, resume_path))
            conn.commit()
            conn.close()

            flash('Application submitted successfully!')
            return redirect(url_for('success'))

        except Exception as e:
            flash(f'Error: {e}')
            return redirect(url_for('apply'))

@app.route('/success')
def success():
    return render_template('success.html')

if __name__ == '__main__':
    app.run(debug=True)
