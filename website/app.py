from flask import Flask, render_template, send_file, request, flash, redirect, url_for
from flask_bootstrap import Bootstrap5
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)
bootstrap = Bootstrap5(app)

# Remove email configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Load project data
def load_projects():
    with open('projects/projects.json') as f:
        return json.load(f)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/projects')
def projects():
    projects = load_projects()
    return render_template('projects.html', projects=projects)

@app.route('/skills')
def skills():
    return render_template('skills.html')

@app.route('/cv')
def cv():
    return render_template('cv.html')

@app.route('/download-cv')
def download_cv():
    cv_path = os.path.join(app.static_folder, 'cv/Umar CV UK.pdf')
    return send_file(cv_path, as_attachment=True)

@app.route('/certifications')
def certifications():
    return render_template('certifications.html')

if __name__ == '__main__':
    app.run(debug=True) 