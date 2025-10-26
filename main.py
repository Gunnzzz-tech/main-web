from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename
from urllib.parse import urlencode

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# --- File upload setup ---
UPLOAD_FOLDER = os.path.join("uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- Database setup ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
os.makedirs(INSTANCE_DIR, exist_ok=True)
DB_PATH = os.path.join(INSTANCE_DIR, "job_portal.db")
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_PATH}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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
    db.create_all()
    print(f"✅ Database ready: {DB_PATH}")

# --- Helper to preserve campaign/query params ---
def preserve_params(default_url='/', extra_params=None):
    """
    Returns a redirect URL that preserves gclid and utm_* parameters.
    """
    params = {}
    # Keep gclid & utm parameters
    for key, value in request.args.items():
        if key.startswith('utm_') or key == 'gclid':
            params[key] = value
    # Add any extra params
    if extra_params:
        params.update(extra_params)
    # Build URL
    if params:
        return f"{default_url}?{urlencode(params)}"
    return default_url

def get_preserved_params():
    """
    Returns a dictionary of preserved parameters for use in templates.
    """
    params = {}
    for key, value in request.args.items():
        if key.startswith('utm_') or key == 'gclid':
            params[key] = value
    return params

# --- Routes ---
@app.route('/', methods=['GET', 'POST'])
def index():
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
        return redirect(preserve_params(url_for('submit')))

    # Pass preserved params to template
    preserved_params = get_preserved_params()
    return render_template('index.html', query_params=preserved_params)

# --- Terms Pages ---
@app.route('/terms/data-collection')
def terms_data_collection():
    preserved_params = get_preserved_params()
    return render_template('terms_data_collection.html', query_params=preserved_params)

@app.route('/terms/communication')
def terms_communication():
    preserved_params = get_preserved_params()
    return render_template('terms_communication.html', query_params=preserved_params)

@app.route('/terms/recruitment')
def terms_recruitment():
    preserved_params = get_preserved_params()
    return render_template('terms_recruitment.html', query_params=preserved_params)

@app.route('/submit')
def submit():
    preserved_params = get_preserved_params()
    return render_template('submit.html', query_params=preserved_params)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/applications')
def applications():
    all_applicants = Applicant.query.order_by(Applicant.submitted_at.desc()).all()
    preserved_params = get_preserved_params()
    return render_template('applications.html', applicants=all_applicants, query_params=preserved_params)

# --- Run App ---
if __name__ == '__main__':
    app.run(debug=True)