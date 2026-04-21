import pandas as pd 
import numpy as np 
from sklearn.model_selection import train_test_split 
from sklearn.linear_model import LinearRegression, LogisticRegression 
from sklearn.tree import DecisionTreeRegressor 
from sklearn.ensemble import RandomForestClassifier 
from sklearn.cluster import KMeans 
from sklearn.metrics import r2_score, mean_squared_error, accuracy_score, silhouette_score 
 
def train_model_logic(df: pd.DataFrame, problem_type: str, algorithm: str, target_col: 
str = None): 
    # 1. Prepare Features (X) and Target (y) 
    if problem_type in ('classification', 'regression'): 
        if not target_col or target_col not in df.columns: 
            raise ValueError(f"Target column '{target_col}' not found in dataset.") 
             
        X = df.drop(columns=[target_col]) 
        y = df[target_col] 
         
        # Split into Train and Test sets (80/20) 
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42) 
    else: 
        # Clustering (Unsupervised) 
        X = df 
        X_train = X 
        X_test = X 
        y_train = None 
        y_test = None 
 
    # 2. Initialize the correct algorithm 
    if algorithm == 'logistic_regression': 
        model = LogisticRegression(max_iter=1000) 
    elif algorithm == 'random_forest': 
        model = RandomForestClassifier(n_estimators=100) 
    elif algorithm == 'linear_regression': 
        model = LinearRegression() 
    elif algorithm == 'decision_tree': 
        model = DecisionTreeRegressor() 
    elif algorithm == 'kmeans': 
        model = KMeans(n_clusters=3, random_state=42, n_init='auto')
    else: 
        raise ValueError(f"Unknown algorithm: {algorithm}") 
 
    # 3. Fit the model 
    model.fit(X_train, y_train) if y_train is not None else model.fit(X_train) 
 
    # 4. Calculate initial metrics 
    metrics = {} 
    if problem_type == 'classification': 
        y_pred = model.predict(X_test) 
        metrics['accuracy'] = round(accuracy_score(y_test, y_pred), 4) 
    elif problem_type == 'regression': 
        y_pred = model.predict(X_test) 
        metrics['r2']   = round(r2_score(y_test, y_pred), 4) 
        metrics['rmse'] = round(np.sqrt(mean_squared_error(y_test, y_pred)), 4) 
    elif problem_type == 'clustering': 
        # Silhouette score requires at least 2 clusters 
        if len(set(model.labels_)) > 1: 
            metrics['silhouette'] = round(silhouette_score(X, model.labels_), 4) 
        else: 
            metrics['silhouette'] = 0 
 
    return model, metrics, X_test, y_test 