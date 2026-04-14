from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# ----------------------
# HOME PAGE
# ----------------------
@app.route('/')
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


# ----------------------
# HANDLE LOGIN (BASIC)
# ----------------------
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    # TEMP logic (replace with DB later)
    if username == "admin" and password == "1234":
        return redirect(url_for('home'))
    else:
        return "Invalid Credentials"

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    # TEMP (later connect DB)
    print(username, email, password)

    return redirect(url_for('auth'))

# ----------------------
# RUN SERVER
# ----------------------
if __name__ == '__main__':
    app.run(debug=True)