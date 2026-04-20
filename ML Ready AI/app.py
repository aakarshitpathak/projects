from flask import Flask, render_template, request, redirect, url_for,session,flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash  
from functools import wraps
import os 
import io 
import pandas as pd 
from flask import (Flask, render_template, request, 
redirect, url_for, flash, session) 
from werkzeug.utils import secure_filename 
from modules.data_loader  import load_dataframe, allowed_file 
from modules.data_summary import get_summary 
from modules.eda import generate_visualizations



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

# ── App config ────────────────────────────────────────────── 
app = Flask(__name__) 
app.secret_key = 'mlreadyai_secret_2025'   # needed for flash & session 
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
            flash('Unsupported file format. Please upload CSV, Excel, JSON, XML or HTML.', 
'error') 
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
    return render_template('summary.html', summary=summary_data, 
filename=filename)

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
 
# ── PLACEHOLDER routes (will be filled in future modules) ─── 
 

""" 
modules/data_loader.py — MODULE 3 
Reads the uploaded file into a Pandas DataFrame. 
Supports: CSV, Excel (.xlsx/.xls), JSON, XML, HTML 
""" 
 
import pandas as pd 
 
# Allowed file extensions 
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'json', 'xml', 'html', 'htm'} 
 
def allowed_file(filename: str) -> bool: 
    """ 
    Check if the uploaded filename has an allowed extension. 
    Returns True if allowed, False otherwise. 
    """ 
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS 
 
def load_dataframe(filepath: str) -> pd.DataFrame:
    ext = filepath.rsplit('.', 1)[1].lower() 
 
    if ext == 'csv': 
        df = pd.read_csv(filepath) 
 
    elif ext in ('xlsx', 'xls'): 
        df = pd.read_excel(filepath) 
 
    elif ext == 'json': 
        df = pd.read_json(filepath) 
 
    elif ext == 'xml': 
        df = pd.read_xml(filepath) 
 
    elif ext in ('html', 'htm'): 
        # read_html returns a list of tables; use the first one 
        tables = pd.read_html(filepath) 
        if not tables: 
            raise ValueError("No HTML table found in the uploaded file.") 
        df = tables[0] 
 
    else:
         raise ValueError(f"Unsupported file format: .{ext}") 
    return df 

""" 
modules/data_summary.py — MODULE 4 
Generates a clean summary of the DataFrame: 
  • Shape (rows × columns) 
  • Column names + data types 
  • Missing value counts 
  • Basic descriptive statistics (describe()) 
""" 

def get_summary(df: pd.DataFrame) -> dict:
    # ── Basic shape ──────────────────────────────────────── 
    rows, cols = df.shape
        # ── Per-column info ──────────────────────────────────── 
    columns_info = [] 
    for col in df.columns: 
        missing_count = int(df[col].isna().sum()) 
        missing_pct   = round((missing_count / rows) * 100, 1) if rows > 0 else 0.0 
        columns_info.append({ 
            'name'        : col, 
            'dtype'       : str(df[col].dtype), 
            'missing'     : missing_count, 
            'missing_pct' : missing_pct, 
        }) 
 
    # ── Descriptive statistics (numeric columns only) ────── 
    # Transpose so each column becomes a row → easier to loop in Jinja 
    desc = df.describe(include='number')    # rows: count mean std min 25% 50% 75% max 
    stats_dict = desc.round(3).to_dict()    # {col_name: {stat: val, ...}} 
 
    # ── Preview (first 5 rows) ───────────────────────────── 
    preview_df   = df.head(5) 
    preview_cols = list(preview_df.columns) 
    # Convert each row to a plain list so Jinja can iterate 
    preview_rows = [list(row) for row in preview_df.values] 
 
    return { 
        'rows'         : rows, 
        'cols'         : cols, 
        'columns_info' : columns_info,
        'stats'        : stats_dict, 
        'preview_cols' : preview_cols, 'preview_rows' : preview_rows, 
}   

""" 
modules/eda.py — MODULE 5 
Generates data visualizations using Matplotlib and Seaborn. 
Plots are converted to Base64 strings to be embedded directly in HTML. 
""" 
 
import matplotlib 
matplotlib.use('Agg')  # Non-interactive backend (essential for Flask) 
import matplotlib.pyplot as plt 
import seaborn as sns 
import io 
import base64 
import pandas as pd 
 
def get_base64_plot(): 
    """Converts the current matplotlib figure to a base64 string.""" 
    buf = io.BytesIO() 
    plt.savefig(buf, format='png', bbox_inches='tight') 
    plt.close() 
    buf.seek(0) 
    return base64.b64encode(buf.getvalue()).decode('utf-8') 
 
def generate_visualizations(df: pd.DataFrame) -> dict:   
    plots = {} 
 
    # Set dark theme for plots to match UI 
    plt.style.use('dark_background') 
    sns.set_palette("husl")  
       # 1. ── Histograms (Numeric Distributions) ────────── 
    numeric_cols = df.select_dtypes(include=['number']).columns 
    if not numeric_cols.empty: 
        # We'll plot up to top 6 numeric columns to keep it clean 
        cols_to_plot = numeric_cols[:6] 
        n = len(cols_to_plot) 
        rows = (n + 1) // 2 
         
        plt.figure(figsize=(12, 4 * rows)) 
        for i, col in enumerate(cols_to_plot): 
            plt.subplot(rows, 2, i + 1) 
            sns.histplot(df[col].dropna(), kde=True, color='#6c63ff') 
            plt.title(f'Distribution of {col}', color='#00d2ff', fontweight='bold') 
            plt.grid(alpha=0.2) 
         
        plt.tight_layout() 
        plots['histograms'] = get_base64_plot()  

    # 2. ── Bar Charts (Categorical Counts) ────────────── 
        cat_cols = df.select_dtypes(include=['object', 'category']).columns 
    if not cat_cols.empty: 
        # Plot up to top 4 categorical columns 
        cols_to_plot = cat_cols[:4] 
        n = len(cols_to_plot) 
        rows = (n + 1) // 2 
 
        plt.figure(figsize=(12, 4 * rows)) 
        for i, col in enumerate(cols_to_plot): 
            plt.subplot(rows, 2, i + 1) 
            # Show top 10 categories only 
            counts = df[col].value_counts().head(10) 
            sns.barplot(x=counts.index, y=counts.values, palette="mako") 
            plt.title(f'Counts of {col} (Top 10)', color='#00d2ff', fontweight='bold') 
            plt.xticks(rotation=45) 
            plt.grid(alpha=0.2, axis='y') 
         
        plt.tight_layout() 
        plots['bar_charts'] = get_base64_plot() 
    
        # 3. ── Correlation Heatmap ────────────────────────── 
    if len(numeric_cols) > 1: 
        plt.figure(figsize=(10, 8)) 
        corr = df[numeric_cols].corr() 
        sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5) 
        plt.title('Feature Correlation Heatmap', color='#00d2ff', fontweight='bold', 
        fontsize=16)
        plt.tight_layout() 
        plots['heatmap'] = get_base64_plot() 
    return plots  



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
                flash(f'✅  Missing values handled using "{strategy}" strategy.', 'success') 
            elif action == 'outliers': 
                df_cleaned = handle_outliers(df, strategy=strategy) 
                set_df(df_cleaned) 
                flash(f'✅  Outliers handled using "{strategy}" strategy.', 'success') 
            elif action == 'duplicates': 
                df_cleaned = remove_duplicates(df) 
                set_df(df_cleaned)
                flash(f'   Duplicate rows removed.', 'success') 
            elif action == 'fix_inconsistent': 
                df_cleaned = fix_inconsistencies(df) 
                set_df(df_cleaned) 
                flash(f'   Basic string inconsistencies fixed.', 'success') 
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
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'error')
            return redirect(url_for('auth'))
        return f(*args, **kwargs)
    return decorated_function


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
            flash('    Please select at least one column.', 'error') 
            return redirect(url_for('feature_engineering')) 
 
        try: 
            if action == 'label_encode': 
                df_new = apply_label_encoding(df, selected_cols) 
                set_df(df_new) 
                flash(f'   Label encoded: {", ".join(selected_cols)}', 'success') 
            elif action == 'scale': 
                df_new = apply_standard_scaling(df, selected_cols) 
                set_df(df_new)
                flash(f'   Scaled: {", ".join(selected_cols)}', 'success') 
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
            flash('    Please select a problem type.', 'error') 
            return redirect(url_for('model')) 
 
        if problem_type in ('classification', 'regression') and not target_col: 
            flash(f'    Prediction for "{problem_type}" requires a Target Column.', 'error') 
            return redirect(url_for('model')) 
 
        # Store in session for Module 11/12 
        session['problem_type'] = problem_type 
        session['target_col']    = target_col 
         
        flash(f'   Problem Type: {problem_type.capitalize()} selected.', 'success') 
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
            flash('    Please select an algorithm.', 'error') 
            return redirect(url_for('algorithm_selection')) 
 
        # Store chosen algorithm in session 
        session['algorithm'] = algorithm 
        flash(f'   Algorithm: {algorithm.replace("_", " ").capitalize()} selected.', 'success') 
         
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
 
    if not df or not algorithm: 
        flash('Data or Algorithm missing. Please restart the process.', 'error') 
        return redirect(url_for('upload')) 
 
    try: 
        # Run the training logic 
        model_obj, metrics, X_test, y_test = train_model_logic(df, problem_type, algorithm, 
target_col) 
         
        # Store model object globally for exporting in Module 14 
        _store['trained_model'] = model_obj 
         
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
    model_obj = _store.get('trained_model') 
    algorithm = session.get('algorithm', 'model') 
     
    if model_obj is None: 
        flash('    No trained model found to export.', 'error') 
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

# ----------------------
# HANDLE LOGIN (BASIC)
# ----------------------
@app.route('/login', methods=['GET', 'POST'])
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