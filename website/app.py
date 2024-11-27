from flask import Flask, render_template, send_file, request, flash, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)
bootstrap = Bootstrap5(app)

# Email Configuration for iCloud
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['MAIL_SERVER'] = 'smtp.mail.me.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
mail = Mail(app)

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

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        try:
            msg = Message(
                subject=f"Portfolio Contact: {subject}",
                sender=('Umar Bhaiyat', 'bhaiyatu@icloud.com'),
                recipients=['bhaiyatu@icloud.com'],
                body=f"From: {name} <{email}>\n\nMessage:\n{message}"
            )
            msg.reply_to = email
            mail.send(msg)
            flash('Your message has been sent successfully!', 'success')
            return redirect(url_for('contact'))
        except Exception as e:
            print(f"Email error: {str(e)}")
            flash('An error occurred while sending your message. Please try again.', 'danger')
            return redirect(url_for('contact'))
    
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True) 