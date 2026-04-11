from flask import Flask, render_template, url_for,session,request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash,generate_password_hash
from flask_login import login_required

app = Flask(__name__)

@app.route('/')
def home():
        return render_template('home.html')

@app.route('/login')
def login():
        return render_template('login.html')

@app.route('/about')
def about():
        return render_template('about.html')

if __name__ == '__main__':
        app.run(debug=True)