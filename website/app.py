from flask import Flask, render_template
from flask_bootstrap import Bootstrap5
import os
import json

app = Flask(__name__)
bootstrap = Bootstrap5(app)

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

if __name__ == '__main__':
    app.run(debug=True) 