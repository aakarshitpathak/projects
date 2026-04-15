from flask import Flask, render_template, request, redirect, url_for,session,flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash  
from functools import wraps



app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flashing messages
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

with app.app_context():
    db.create_all()

# ----------------------
# HOME PAGE
# ----------------------
@app.route('/')
def landing():
    return render_template('landing.html')
@app.route('/home')
def home():
    return render_template('home.html')

# ----------------------
# ABOUT PAGE
# ----------------------
@app.route('/about')
def about():
    return render_template('about.html')


# ----------------------
# AUTH PAGE (LOGIN/SIGNUP)
# ----------------------
@app.route('/auth')
def auth():
    return render_template('authentication.html')
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'error')
            return redirect(url_for('auth'))
        return f(*args, **kwargs)
    return decorated_function

# ----------------------
# HANDLE LOGIN (BASIC)
# ----------------------
@app.route('/login', methods=['POST'])
def login():
    if request.method=='POST':
                email=request.form['email']
                password=request.form['password']
                user=User.query.filter_by(email=email).first()
                if user and check_password_hash(user.password,password):
                        session['user_id']=user.id
                        session['user_name']=user.name
                        flash('Signin successful','success')
                        return redirect(url_for('home'))
    else:
        flash("Invalid Credentials", "error")
        return redirect(url_for('auth'))


@app.route('/signup', methods=['POST'])
def signup():
    if request.method=='POST':
                name=request.form['name']
                email=request.form['email']
                password=request.form['password']
                confirm_password=request.form['confirm_password']

                if not name or len(name.strip())<2:
                        flash('name must be atleast 2 character long','error')
                        return redirect(url_for('auth'))
                if not email or '@' not in email :
                        flash('Invalid email','error')
                        return redirect(url_for('auth'))
                if not password or len(password)<8 or not any(char.isalpha() for char in password ) or not any(char.isdigit() for char in password) or not any (not char.isalnum() for char in password):
                        flash('pass must be atleast 8 char long and contain letters and contain numbers and special characters','error')
                        return redirect(url_for('auth'))
                if confirm_password!=password:
                        flash('Confirm password should match password','error')
                        return redirect(url_for('auth'))
                #check if user already exists
                existing_user=User.query.filter_by(email=email).first()

                if existing_user:
                        flash('Email already exists.Please login. ','error')
                        return redirect(url_for('auth'))
                # generate hash password
                hashed_password=generate_password_hash(password)
                new_user=User(
                        name=name.strip(),
                        email=email.strip(),
                        password=hashed_password
                )
                try:
                        db.session.add(new_user)
                        db.session.commit()
                        flash('Registration successful .Proceed to signin','success')
                        return redirect(url_for('auth'))
                except Exception as e:
                        db.session.rollback()
                        flash('Some error occured while registering','error')
                        return redirect(url_for('auth'))

# ----------------------
# RUN SERVER
# ----------------------
if __name__ == '__main__':
    app.run(debug=True)