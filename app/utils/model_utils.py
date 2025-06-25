import pandas as pd
import os
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
from joblib import dump, load

def train_and_save_model(csv_path):
    df = pd.read_csv(csv_path)
    numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
    df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].mean())

    categorical_columns = df.select_dtypes(include=['object', 'category']).columns
    for column in categorical_columns:
        df[column] = df[column].fillna(df[column].mode()[0])

    df = pd.get_dummies(df, columns=['Gender', 'Marital Status', 'Work Status', 'Residence', 'Smoking Status'], drop_first=True)
    numeric_features = ['Age', 'BMI', 'Hypertension', 'Heart Disease', 'Avg Glucose Level']
    encoded_features = [col for col in df.columns if '_' in col]
    selected_features = numeric_features + encoded_features

    X = df[selected_features]
    y = df['Stroke Outcome']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = LogisticRegression(max_iter=1000, class_weight='balanced')
    param_grid = {'C': [0.1, 1, 10, 100]}
    grid_search = GridSearchCV(model, param_grid, cv=5, scoring='f1')
    grid_search.fit(X_train_scaled, y_train)

    best_model = grid_search.best_estimator_
    print("Best Model Parameters:", grid_search.best_params_)
    y_scores = best_model.predict_proba(X_test_scaled)[:, 1]
    y_pred_adjusted = (y_scores >= 0.55).astype(int)
    print("Model Accuracy: {:.2f}%".format(accuracy_score(y_test, y_pred_adjusted) * 100))
    print(classification_report(y_test, y_pred_adjusted))

    os.makedirs('models', exist_ok=True)
    dump(best_model, 'models/model.pkl')
    dump(scaler, 'models/scaler.pkl')
    dump(selected_features, 'models/features.pkl')



def load_model_components():
    return(
        load('models/model.pkl'),
        load('models/scaler.pkl'),
        load('models/features.pkl')
    )