from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# --- File upload setup ---
UPLOAD_FOLDER = os.path.join("uploads")  # relative to project
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- Database setup ---
# --- Database setup ---
# --- Database setup ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
os.makedirs(INSTANCE_DIR, exist_ok=True)

# Prefer instance/job_portal.db, fallback to root
DB_PATH = os.path.join(INSTANCE_DIR, "job_portal.db")
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_PATH}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

with app.app_context():
    db.create_all()
    print(f"✅ Database ready: {DB_PATH}")


# --- Database Model ---
class Applicant(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(150))
    phone = db.Column(db.String(50))
    country = db.Column(db.String(100))
    city = db.Column(db.String(100))
    address = db.Column(db.String(255))
    position = db.Column(db.String(100))
    additional_info = db.Column(db.Text)
    resume_filename = db.Column(db.String(255))
    submitted_at = db.Column(db.DateTime, server_default=db.func.now())

with app.app_context():
    db.create_all()  # creates tables if not exist

# --- Routes ---
@app.route('/')
def index():
    return render_template('home.html')

@app.route('/apply', methods=['POST', 'GET'])
def apply():
    if request.method == 'POST':
        form = request.form
        file = request.files.get('resume')

        resume_filename = None
        if file and file.filename:
            resume_filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], resume_filename)
            file.save(file_path)
        else:
            file_path = None

        # Save to DB
        applicant = Applicant(
            first_name=form.get('first_name'),
            last_name=form.get('last_name'),
            email=form.get('email'),
            phone=form.get('phone'),
            country=form.get('country'),
            city=form.get('city'),
            address=form.get('address'),
            position=form.get('position'),
            additional_info=form.get('additional_info'),
            resume_filename=resume_filename
        )
        db.session.add(applicant)
        db.session.commit()

        flash("Application submitted successfully!")
        return redirect(url_for('success'))

    # If GET, just show the form
    return render_template('index.html')

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/applications')
def view_applications():
    applications = Applicant.query.order_by(Applicant.submitted_at.desc()).all()
    return render_template('applications.html', applications=applications)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
