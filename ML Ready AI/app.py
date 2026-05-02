# ============================================================
# ML READY AI — Main Flask Application
# Modules Completed: All (1-15)
# ============================================================

import os
import io
import pandas as pd
import joblib
from flask import (Flask, render_template, request,
                   redirect, url_for, flash, session, send_from_directory, send_file)
from werkzeug.utils import secure_filename

from modules.data_loader  import load_dataframe, allowed_file
from modules.data_summary import get_summary
from modules.eda          import generate_visualizations
from modules.cleaning     import (handle_missing_values, get_missing_stats, 
                             detect_outliers, handle_outliers,
                             remove_duplicates, fix_inconsistencies)
from modules.feature_engineering import apply_label_encoding, apply_standard_scaling, get_feature_info
from modules.model_training      import train_model_logic
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# ── App config ──────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = 'mlreadyai_secret_2025'   # needed for flash & session

# ── Database config ─────────────────────────────────────────
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

with app.app_context():
    db.create_all()

# ── Authentication Routes ───────────────────────────────────

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handle user registration."""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('login'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered.', 'error')
            return redirect(url_for('login'))

        hashed_password = generate_password_hash(password)
        new_user = User(name=name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('authentication.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for('upload'))
        else:
            flash('Invalid email or password.', 'error')
            return redirect(url_for('login'))

    if 'user_id' in session:
        return redirect(url_for('upload'))
    return render_template('authentication.html')

@app.route('/logout')
def logout():
    """Handle user logout."""
    session.pop('user_id', None)
    session.pop('user_name', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

def login_required(f):
    """Decorator to require login for protected routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Folder where uploaded files are stored temporarily
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024   # 50 MB limit

# In-memory store for the current DataFrame (simple global)
# We use a dict so it can be updated from any route
_store = {}


def get_df() -> pd.DataFrame | None:
    """Return the currently loaded DataFrame (or None)."""
    return _store.get('df')


def set_df(df: pd.DataFrame):
    """Save a DataFrame into the in-memory store."""
    _store['df'] = df


# ── MODULE 1 — Home ─────────────────────────────────────────
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


# ── MODULE 2 & 3 — Upload + Parse ───────────────────────────
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """
    GET  → show the upload form
    POST → receive the file, parse it into a DataFrame, store it
    """
    if request.method == 'POST':
        # 1. Check a file was included in the form
        if 'dataset' not in request.files:
            flash('No file part in the request.', 'error')
            return redirect(url_for('upload'))

        file = request.files['dataset']

        # 2. Check the user actually selected a file
        if file.filename == '':
            flash('Please select a file before uploading.', 'error')
            return redirect(url_for('upload'))

        # 3. Validate extension
        if not allowed_file(file.filename):
            flash('Unsupported file format. Please upload CSV, Excel, JSON, XML or HTML.', 'error')
            return redirect(url_for('upload'))

        # 4. Save the file safely
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # 5. Parse the file into a DataFrame (MODULE 3)
        try:
            df = load_dataframe(filepath)
        except Exception as e:
            flash(f'Could not read file: {e}', 'error')
            return redirect(url_for('upload'))

        # 6. Store in memory and remember the filename in session
        set_df(df)
        session['filename'] = filename

        flash(f'✅ "{filename}" uploaded successfully — {df.shape[0]} rows × {df.shape[1]} columns.', 'success')
        return redirect(url_for('summary'))   # → Module 4

    # GET request → just show the upload form
    return render_template('upload.html')


# ── MODULE 4 — Data Summary ─────────────────────────────────
@app.route('/summary')
def summary():
    """
    Shows:
      • Key metrics (rows, cols, missing cols, numeric cols)
      • Per-column info table (name, dtype, missing count/pct)
      • Descriptive statistics for numeric columns
      • First 5 rows preview
    """
    df = get_df()
    if df is None:
        flash('Please upload a dataset first.', 'error')
        return redirect(url_for('upload'))

    summary_data = get_summary(df)
    filename     = session.get('filename', 'dataset')
    return render_template('summary.html', summary=summary_data, filename=filename)


# ── MODULE 5 — EDA Visualizations ───────────────────────────
@app.route('/eda')
def eda():
    """
    Generates and displays:
      • Histograms for numeric columns
      • Bar charts for categorical columns
      • Correlation Heatmap
    Uses Base64 encoding to embed plots directly in HTML.
    """
    df = get_df()
    if df is None:
        flash('Please upload a dataset first.', 'error')
        return redirect(url_for('upload'))

    plots    = generate_visualizations(df)
    filename = session.get('filename', 'dataset')
    return render_template('eda.html', plots=plots, filename=filename)


# ── MODULE 6 — Missing Value Handling ──────────────────────
@app.route('/cleaning', methods=['GET', 'POST'])
def cleaning():
    """
    Detects missing values and allows the user to fill them.
    """
    df = get_df()
    if df is None:
        flash('Please upload a dataset first.', 'error')
        return redirect(url_for('upload'))

    if request.method == 'POST':
        action   = request.form.get('action')
        strategy = request.form.get('strategy', '')
        
        try:
            if action == 'impute':
                df_cleaned = handle_missing_values(df, strategy=strategy)
                set_df(df_cleaned)
                flash(f'✅ Missing values handled using "{strategy}" strategy.', 'success')
            elif action == 'outliers':
                df_cleaned = handle_outliers(df, strategy=strategy)
                set_df(df_cleaned)
                flash(f'✅ Outliers handled using "{strategy}" strategy.', 'success')
            elif action == 'duplicates':
                df_cleaned = remove_duplicates(df)
                set_df(df_cleaned)
                flash(f'✅ Duplicate rows removed.', 'success')
            elif action == 'fix_inconsistent':
                df_cleaned = fix_inconsistencies(df)
                set_df(df_cleaned)
                flash(f'✅ Basic string inconsistencies fixed.', 'success')
        except Exception as e:
            flash(f'Error during cleaning: {e}', 'error')
        
        return redirect(url_for('cleaning'))

    missing_stats = get_missing_stats(df)
    outlier_stats = detect_outliers(df)
    duplicate_count = int(df.duplicated().sum())
    
    return render_template('cleaning.html', 
                          missing_stats=missing_stats, 
                          outlier_stats=outlier_stats,
                          duplicate_count=duplicate_count)


# ── MODULE 9 — Feature Engineering ───────────────────────
@app.route('/feature_engineering', methods=['GET', 'POST'])
def feature_engineering():
    """
    Transforms categorical strings to numbers and scales numeric features.
    """
    df = get_df()
    if df is None:
        flash('Please upload a dataset first.', 'error')
        return redirect(url_for('upload'))

    if request.method == 'POST':
        action   = request.form.get('action')
        selected_cols = request.form.getlist('cols')  # Get list of checked columns
        
        if not selected_cols:
            flash('⚠️ Please select at least one column.', 'error')
            return redirect(url_for('feature_engineering'))

        try:
            if action == 'label_encode':
                df_new = apply_label_encoding(df, selected_cols)
                set_df(df_new)
                flash(f'✅ Label encoded: {", ".join(selected_cols)}', 'success')
            elif action == 'scale':
                df_new = apply_standard_scaling(df, selected_cols)
                set_df(df_new)
                flash(f'✅ Scaled: {", ".join(selected_cols)}', 'success')
        except Exception as e:
            flash(f'Error during feature engineering: {e}', 'error')
        
        return redirect(url_for('feature_engineering'))

    feature_info = get_feature_info(df)
    return render_template('feature_engineering.html', features=feature_info)


# ── MODULE 10 — ML Problem Selection ──────────────────────
@app.route('/model', methods=['GET', 'POST'])
def model():
    """
    Step 1: User selects the ML problem type (Classification / Regression / Clustering).
    Step 2: User selects the target column (for supervised problems).
    Selection is stored in session to be used by the following modules.
    """
    df = get_df()
    if df is None:
        flash('Please upload a dataset first.', 'error')
        return redirect(url_for('upload'))

    if request.method == 'POST':
        problem_type = request.form.get('problem_type')
        target_col    = request.form.get('target_col', '')
        
        if not problem_type:
            flash('⚠️ Please select a problem type.', 'error')
            return redirect(url_for('model'))

        if problem_type in ('classification', 'regression') and not target_col:
            flash(f'⚠️ Prediction for "{problem_type}" requires a Target Column.', 'error')
            return redirect(url_for('model'))

        # Store in session for Module 11/12
        session['problem_type'] = problem_type
        session['target_col']    = target_col
        
        flash(f'✅ Problem Type: {problem_type.capitalize()} selected.', 'success')
        # → Module 11 Algorithm Selection
        return redirect(url_for('algorithm_selection'))

    columns = list(df.columns)
    return render_template('model.html', columns=columns)


# ── MODULE 11 — Algorithm Selection ──────────────────────────
@app.route('/algorithm_selection', methods=['GET', 'POST'])
def algorithm_selection():
    """
    Shows a list of algorithms appropriate for the selected problem type.
    """
    problem_type = session.get('problem_type')
    if not problem_type:
        flash('Please select a problem type first.', 'error')
        return redirect(url_for('model'))

    if request.method == 'POST':
        algorithm = request.form.get('algorithm')
        if not algorithm:
            flash('⚠️ Please select an algorithm.', 'error')
            return redirect(url_for('algorithm_selection'))

        # Store chosen algorithm in session
        session['algorithm'] = algorithm
        flash(f'✅ Algorithm: {algorithm.replace("_", " ").capitalize()} selected.', 'success')
        
        # → Module 12: Training
        return redirect(url_for('train_model'))

    return render_template('algorithm.html', problem_type=problem_type)


# ── MODULE 12 & 13 — Model Training & Evaluation ──────────
@app.route('/train_model')
def train_model():
    """
    Step 1: Get selected algorithm and data.
    Step 2: Train the model using scikit-learn.
    Step 3: Calculate metrics and show the result page.
    """
    df = get_df()
    problem_type = session.get('problem_type')
    algorithm    = session.get('algorithm')
    target_col   = session.get('target_col')

    if df is None or not algorithm:
        flash('Data or Algorithm missing. Please restart the process.', 'error')
        return redirect(url_for('upload'))

    try:
        # Run the training logic
        model_obj, metrics, X_test, y_test = train_model_logic(df, problem_type, algorithm, target_col)
        
        # Store model object and metrics globally for exporting
        _store['trained_model'] = model_obj
        _store['metrics']       = metrics
        
        # Format metrics and render the result page (Module 13)
        return render_template('result.html', 
                               metrics=metrics, 
                               algorithm=algorithm, 
                               problem_type=problem_type)
    except Exception as e:
        flash(f'Error during training: {e}', 'error')
        return redirect(url_for('algorithm_selection'))


# ── MODULE 14 — Model Export ────────────────────────────────
@app.route('/export_model')
def export_model():
    """
    Saves the trained model using joblib and provides it as a download.
    """
    model_obj = _store.get('trained_model')
    algorithm = session.get('algorithm', 'model')
    
    if model_obj is None:
        flash('⚠️ No trained model found to export.', 'error')
        return redirect(url_for('train_model'))

    try:
        # 1. Define filename and path
        models_dir = os.path.join(os.path.dirname(__file__), 'models')
        os.makedirs(models_dir, exist_ok=True)
        filename = f"{algorithm}_trained.pkl"
        filepath = os.path.join(models_dir, filename)
        
        # 2. Save the model using joblib
        joblib.dump(model_obj, filepath)
        
        # 3. Provide as download
        return send_from_directory(directory=models_dir, path=filename, as_attachment=True)
        
    except Exception as e:
        flash(f'Error exporting model: {e}', 'error')
        return redirect(url_for('train_model'))


# ── MODULE 15 — ML-Ready Dataset Export & Dashboard ─────────
@app.route('/export_data')
def export_data():
    """
    Exports the currently cleaned and processed DataFrame as a CSV file.
    """
    df = get_df()
    if df is None:
        flash('⚠️ No data found to export.', 'error')
        return redirect(url_for('upload'))

    try:
        # Generate CSV in memory
        output = io.BytesIO()
        df.to_csv(output, index=False)
        output.seek(0)
        
        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name='ml_ready_cleaned_data.csv'
        )
    except Exception as e:
        flash(f'Error exporting data: {e}', 'error')
        return redirect(url_for('final_dashboard'))


@app.route('/final')
def final_dashboard():
    """
    Shows a summary of all completed steps and final metrics.
    """
    problem_type = session.get('problem_type')
    algorithm    = session.get('algorithm')
    metrics      = _store.get('metrics')

    if not algorithm or not metrics:
        flash('⚠️ Training metrics missing. Please train a model first.', 'error')
        return redirect(url_for('train_model'))

    return render_template('final.html', 
                          problem_type=problem_type, 
                          algorithm=algorithm, 
                          metrics=metrics)



# ── PLACEHOLDER routes (will be filled in future modules) ───


# ── Run ─────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True)
