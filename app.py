from flask import Flask, render_template, request, session, redirect, url_for, flash
from config import Config
from models import db, User
import re
import hashlib

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

@app.before_request
def create_tables():
    db.create_all()

def add_user(first_name, last_name, email, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    try:
        new_user = User(first_name=first_name, last_name=last_name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return False
    return True

def check_password(email, password):
    hashed_input_password = hashlib.sha256(password.encode()).hexdigest()
    user = User.query.filter_by(email=email).first()
    return user and hashed_input_password == user.password

@app.route('/')
def index():
    return redirect(url_for('signup'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        warnings = []

        if not re.search(r'[a-z]', password):
            warnings.append("Your password must include at least one lowercase letter.")
        if not re.search(r'[A-Z]', password):
            warnings.append("Your password must include at least one uppercase letter.")
        if not re.search(r'\d', password):
            warnings.append("Your password must include at least one digit.")
        if len(password) < 8:
            warnings.append("Your password must be at least 8 characters long.")
        if not password[-1].isdigit():
            warnings.append("Your password must end with a number.")
        if password != confirm_password:
            warnings.append("Passwords do not match!")

        if warnings:
            return render_template('signup.html', warnings=warnings)
        elif add_user(first_name, last_name, email, password):
            return render_template('thankyou.html')
        else:
            warnings.append("The email is already registered. Please use a different email.")
            return render_template('signup.html', warnings=warnings)
    return render_template('signup.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if check_password(email, password):
            session['email'] = email
            return render_template('secretPage.html')
        else:
            flash("Invalid credentials!", "danger")
            return redirect(url_for('signin'))
    return render_template('signin.html')

if __name__ == '__main__':
    app.run(debug=True)
