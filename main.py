from flask import url_for, Flask, render_template, redirect, request, session, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import os, uuid
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler

import os
from dotenv import load_dotenv  

from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer

app = Flask(__name__)
CORS(app)

load_dotenv()
# ------------------------
# Configuration
# ------------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:2286@localhost/stroke_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '2286'
db = SQLAlchemy(app)

# ------------------------
# EMAIL Configuration
# ------------------------
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')        # Replace with your email password
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')

# Initialize Flask-Mail
mail = Mail(app)

# Initialize serializer for tokens
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])


# ------------------------
# Models
# ------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    date_created = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    hashed_password = db.Column(db.Text, nullable=False)  # Changed from String(200) to Text


class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    hashed_password = db.Column(db.String(255), nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    experience = db.Column(db.Integer, nullable=False)
    specialty = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    contact = db.Column(db.String(50), nullable=False)
    aadhar_no = db.Column(db.String(12), unique=True, nullable=False)
    photo = db.Column(db.String(255), nullable=False)
    degree_doc = db.Column(db.String(255), nullable=False)
    aadhar_doc = db.Column(db.String(255), nullable=False)

# New model for Hospitals
class Hospital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # my_unknown_column = db.Column(db.String(100), nullable=True)  # optional column
    hospital = db.Column(db.String(100), nullable=False)          # hospital name
    state = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    local_address = db.Column(db.String(255), nullable=True)
    pincode = db.Column(db.String(20), nullable=True)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    hashed_password = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now(timezone.utc))


# ------------------------
# File Upload Configuration (for doctor registration)
# ------------------------
BASE_UPLOAD_FOLDER = 'uploads/'
FOLDERS = {
    'photo': os.path.join(BASE_UPLOAD_FOLDER, 'photos'),
    'degree': os.path.join(BASE_UPLOAD_FOLDER, 'degrees'),
    'aadhar': os.path.join(BASE_UPLOAD_FOLDER, 'aadhar')
}
for folder in FOLDERS.values():
    os.makedirs(folder, exist_ok=True)
app.config['UPLOAD_FOLDER'] = BASE_UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file, folder):
    if file and allowed_file(file.filename):
        filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
        filepath = os.path.join(FOLDERS[folder], filename)
        file.save(filepath)
        return filename
    return None

# ------------------------
# Stroke Prediction Model Training
# ------------------------
def train_model():
    # Update the path to your CSV file as needed
    df = pd.read_csv(r'D:\Workspace\stroke prediction\modified_learning_dataset.csv')

    # Fill missing numeric values with the mean
    numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
    df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].mean())

    # Fill missing categorical values with the mode
    categorical_columns = df.select_dtypes(include=['object', 'category']).columns
    for column in categorical_columns:
        df[column] = df[column].fillna(df[column].mode()[0])

    # One-Hot Encode categorical variables (drop_first to avoid multicollinearity)
    df = pd.get_dummies(df, columns=['Gender', 'Marital Status', 'Work Status', 'Residence', 'Smoking Status'], drop_first=True)
    print("Columns after encoding:", df.columns)

    # Select features
    numeric_features = ['Age', 'BMI', 'Hypertension', 'Heart Disease', 'Avg Glucose Level']
    encoded_features = [col for col in df.columns if '_' in col]
    selected_features = numeric_features + encoded_features

    X = df[selected_features]
    y = df['Stroke Outcome']

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Logistic Regression with balanced class weight
    model = LogisticRegression(max_iter=1000, class_weight='balanced')
    param_grid = {'C': [0.1, 1, 10, 100]}
    grid_search = GridSearchCV(model, param_grid, cv=5, scoring='f1')
    grid_search.fit(X_train_scaled, y_train)
    best_model = grid_search.best_estimator_
    print("Best Model Parameters:", grid_search.best_params_)

    #  Evaluate the model
    y_scores = best_model.predict_proba(X_test_scaled)[:, 1]
    threshold = 0.55
    y_pred_adjusted = (y_scores >= threshold).astype(int)
    print("Model Accuracy: {:.2f}%".format(accuracy_score(y_test, y_pred_adjusted) * 100))
    print(classification_report(y_test, y_pred_adjusted))

    return best_model, scaler, selected_features

print("Training prediction model ...")
best_model, scaler, selected_features = train_model()
print("Prediction model trained successfully.")

# ------------------------
# Routes
# ------------------------


# Landing Page (directs to different login pages)
@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/info')
def info():
    return render_template('info.html')


# Login & Registration route (index)
@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if 'username' in session:
        return redirect(url_for('chatbot'))
    if request.method == 'POST':
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'message': 'Invalid JSON payload'}), 400

        form_type = data.get('form_type')
        if form_type == "register":
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            hashed_password = generate_password_hash(password)

             
            if User.query.filter_by(username=username).first():
                return jsonify({'success': False, 'message': 'Username already taken.'}), 400
            
            if User.query.filter(User.email == email).first():  # Case-sensitive email check
                return jsonify({'success': False, 'message': 'Email already registered.'}), 400


            if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
                return jsonify({'success': False, 'message': 'User already exists.'}), 400
            new_user = User(username=username, email=email, hashed_password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Registration successful!'})
        elif form_type == "login":
            email = data.get('email')
            password = data.get('password')
            found_user = User.query.filter_by(email=email).first()
            if found_user and check_password_hash(found_user.hashed_password, password):
                session['username'] = found_user.username
                return jsonify({'success': True, 'message': 'Login successful!'})
            else:
                return jsonify({'success': False, 'message': 'Invalid email or password.'}), 401
    return render_template('index.html')

# Delete user
@app.route('/user_delete')
def user_delete():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized access'}), 401
    del_user = session['username']
    user = User.query.filter_by(username=del_user).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        session.clear()
        return jsonify({'success': True, 'message': 'User deleted successfully!'})
    return redirect(url_for('clrsession'))

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        # Check for the email in all tables
        user = User.query.filter_by(email=email).first()
        doctor = Doctor.query.filter_by(email=email).first()
        admin = Admin.query.filter_by(email=email).first()

        # Use the first found account
        account = user or doctor or admin

        if account:
            # Generate a secure token valid for 1 hour
            token = s.dumps(email, salt='password-reset-salt')
            reset_url = url_for('reset_password', token=token, _external=True)

            # Use account.username if exists, otherwise account.name
            name = getattr(account, 'username', None) or getattr(account, 'name', 'User')

            subject = "Password Reset Request"
            body = f"""
Hi {name},

You requested a password reset. Click the link below to reset your password:
{reset_url}

If you did not make this request, please ignore this email.

Regards,
Your App Team
"""
            msg = Message(subject, recipients=[email], body=body)
            mail.send(msg)
            return render_template('forgot_password.html', message="A password reset link has been sent to your email.")
        else:
            return render_template('forgot_password.html', message="Email not found.")
    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=3600)  # Valid for 1 hour
    except Exception as e:
        return "The reset link is invalid or has expired.", 400

    # Search for the account in all tables
    account = User.query.filter_by(email=email).first() or \
              Doctor.query.filter_by(email=email).first() or \
              Admin.query.filter_by(email=email).first()

    if not account:
        return "User not found.", 404

    if request.method == 'POST':
        new_password = request.form.get('password')
        if not new_password or len(new_password) < 8:
            return render_template('reset_password.html', token=token, message="Password must be at least 8 characters.")
        
        # Update the account's password hash
        account.hashed_password = generate_password_hash(new_password)
        db.session.commit()
        return redirect(url_for('landing'))  # Redirect to landing/login page after reset

    return render_template('reset_password.html', token=token)



# Admin Registration Route
@app.route('/admin_register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        data = request.get_json()  # Expecting JSON payload
        if not data:
            return jsonify({'success': False, 'message': 'Invalid JSON payload'}), 400
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        hashed_password = generate_password_hash(password)
        
        # Check if admin already exists
        if Admin.query.filter((Admin.username == username) | (Admin.email == email)).first():
            return jsonify({'success': False, 'message': 'Admin already exists.'}), 400
        
        new_admin = Admin(username=username, email=email, hashed_password=hashed_password)
        db.session.add(new_admin)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Admin registration successful!'})
    
    # GET: render admin registration page
    return render_template('admin_register.html')


# Admin Login Route
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if 'admin' in session:
        return redirect(url_for('admin_dashboard'))
    else:
        if request.method == 'POST':
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'message': 'Invalid JSON payload'}), 400
        
            email = data.get('email')
            password = data.get('password')
            admin = Admin.query.filter_by(email=email).first()
            if admin and check_password_hash(admin.hashed_password, password):
                session['admin'] = admin.id
                return jsonify({'success': True, 'message': 'Admin login successful!'})
            else:
                return jsonify({'success': False, 'message': 'Invalid email or password.'}), 401
    
        # GET: render admin login page
        return render_template('admin_login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    
    # Query all users and doctors from the database
    users = User.query.all()
    doctors = Doctor.query.all()
    
    return render_template('admin_dashboard.html', users=users, doctors=doctors)

@app.route('/delete_user/<int:user_id>', methods=['DELETE'])
def delete_user_by_admin(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'success': True, 'message': 'User deleted successfully!'})
    else:
        return jsonify({'success': False, 'message': 'User not found.'}), 404

@app.route('/delete_doctor/<int:doctor_id>', methods=['DELETE'])
def delete_doctor_by_admin(doctor_id):
    doctor = Doctor.query.get(doctor_id)
    if doctor:
        db.session.delete(doctor)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Doctor deleted successfully!'})
    else:
        return jsonify({'success': False, 'message': 'Doctor not found.'}), 404


# Chatbot page
@app.route('/chatbot')
def chatbot():
    if 'username' in session:
        return render_template('chatbot.html', username=session['username'])
    else:
        session.clear()
        return redirect(url_for('landing'))

@app.route('/submit_chatbot', methods=['POST'])
def submit_chatbot():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON payload'}), 400

    # For example, assume chatbot sends 'height' and 'weight'
    try:
        height_cm = float(data.get('What is your height in centimeters ?', 0))
        weight_kg = float(data.get('What is your weight in kilograms ?', 0))
        if height_cm > 0 and weight_kg > 0:
            height_m = height_cm / 100.0
            bmi = weight_kg / (height_m * height_m)
            print("BMI:",bmi)
        else:
            print(data)
            bmi = 24.5  # default if missing or invalid
    except Exception as e:
        bmi = 24.5  # default value in case of error

    # Store chatbot data and computed BMI in session for later use
    session['chatbot_data'] = data
    session['bmi'] = bmi

    return jsonify({'success': True, 'message': 'Chatbot data received', 'bmi': bmi})


# Clear session (logout)
@app.route('/clear_session')
def clrsession():
    session.clear()
    return redirect(url_for('chatbot'))

# Report page: Query doctors and hospitals from the database
@app.route('/report')
def report():
    if 'username' not in session:
        return redirect(url_for('user_login'))
    
    # Retrieve chatbot data and compute BMI from chatbot responses.
    chatbot_data = session.get('chatbot_data', {})
    try:
        age = float(chatbot_data.get("Hello, user! Could you please share your age in years?", 0))
    except ValueError:
        age = 0

    try:
        height_cm = float(chatbot_data.get("What is your height in centimeters ?", 0))
        weight_kg = float(chatbot_data.get("What is your weight in kilograms ?", 0))
        bmi = weight_kg / ((height_cm / 100.0) ** 2) if height_cm > 0 and weight_kg > 0 else 24.5
    except ValueError:
        bmi = 24.5

    hypertension = 1 if chatbot_data.get("Have you ever been diagnosed with high blood pressure or hypertension?", "No").strip().lower() == "yes" else 0
    heart_disease = 1 if chatbot_data.get("Lastly, have you ever been diagnosed with any heart-related conditions or heart disease?", "No").strip().lower() == "yes" else 0
    try:
        avg_glucose = float(chatbot_data.get("Could you please provide your average glucose level?", 0))
    except ValueError:
        avg_glucose = 0

    gender_response = chatbot_data.get("Are you biologically male or female?", "").strip().lower()
    marital_status = chatbot_data.get("What is your Martial Status?", "").strip().lower()
    work_status = chatbot_data.get("Can you let me know your current work type?", "").strip().lower()
    residence = chatbot_data.get("Could you describe your living environment?", "").strip().lower()
    smoking_status = chatbot_data.get("What is your smoking status?", "").strip().lower()

    model_input = {
        "Age": age,
        "BMI": bmi,
        "Hypertension": hypertension,
        "Heart Disease": heart_disease,
        "Avg Glucose Level": avg_glucose,
        "Gender_Male": 1 if gender_response == "male" else 0,
        "Marital Status_Single": 1 if marital_status == "single" else 0,
        "Work Status_Government": 1 if work_status == "government" else 0,
        "Work Status_Student/Dependent": 1 if work_status == "student/dependent" else 0,
        "Work Status_Unemployed": 1 if work_status == "unemployed" else 0,
        "Residence_Urban": 1 if residence == "urban" else 0,
        "Smoking Status_Former Smoker": 1 if smoking_status == "former smoker" else 0,
        "Smoking Status_Never Smoked": 1 if smoking_status == "never smoked" else 0,
        "Smoking Status_Unknown": 1 if smoking_status == "unknown" else 0,
    }
    
    for feature in selected_features:
        if feature not in model_input:
            model_input[feature] = 0

    input_df = pd.DataFrame([model_input], columns=selected_features)
    input_scaled = scaler.transform(input_df)
    prob = best_model.predict_proba(input_scaled)[:, 1][0]
    user_prediction_percentage = round(prob * 100, 2)
    threshold = 0.55
    risk_label = "High Risk" if prob >= threshold else "Low/Moderate Risk"
    
    # Query hospitals and doctors (omitting unchanged parts)
    hospitals_query = Hospital.query.all()
    hospitals = [{
        "id": h.id,
        "name": h.hospital,
        "state": h.state,
        "city": h.city,
        "address": h.local_address,
        "pincode": h.pincode
    } for h in hospitals_query]
    
    doctors_query = Doctor.query.all()
    doctors = [{
        "name": d.name,
        "email": d.email,
        "gender": d.gender,
        "experience": d.experience,
        "specialty": d.specialty,
        "contact": d.contact,
        "location": d.location
    } for d in doctors_query]
    
    return render_template('report.html',
                           bmi=round(bmi,2),
                           user_prediction_label=risk_label,
                           user_prediction_percentage=user_prediction_percentage,
                           hospitals=hospitals,
                           doctors=doctors)





# API endpoint: Filter hospitals (from database)
@app.route('/filter/hospitals', methods=['GET'])
def filter_hospitals_route():
    name = request.args.get('name', '')
    state = request.args.get('hospitalRegion', '')
    hospitals = Hospital.query.filter(
        Hospital.hospital.ilike(f"%{name}%"),
        Hospital.state.ilike(f"%{state}%")
    ).all()
    result = [{
        "id": h.id,
        "name": h.hospital,
        "state": h.state,
        "city": h.city,
        "address": h.local_address,
        "pincode": h.pincode
    } for h in hospitals]
    return jsonify(result)


# API endpoint: Filter doctors (from database)
@app.route('/filter/doctors', methods=['GET'])
def filter_doctors_route():
    name = request.args.get('name', '')
    speciality = request.args.get('speciality', '')
    doctors = Doctor.query.filter(
        Doctor.name.ilike(f"%{name}%"),
        Doctor.specialty.ilike(f"%{speciality}%")
    ).all()
    result = [{
        "id": d.id,
        "name": d.name,
        "email": d.email,
        "gender": d.gender,
        "experience": d.experience,
        "specialty": d.specialty,  # note the consistent spelling
        "contact": d.contact,
        "location": d.location
    } for d in doctors]
    return jsonify(result)


# Serve uploaded files for doctor registration
@app.route('/uploads/<folder>/<filename>')
def serve_file(folder, filename):
    if folder not in FOLDERS:
        return jsonify({"message": "Invalid folder!"}), 403
    return send_from_directory(FOLDERS[folder], filename)


# Doctor Login Route
@app.route('/doctor_login', methods=['GET', 'POST'])
def doctor_login():
    if request.method == 'POST':
        data = request.get_json()  # Expecting JSON payload from the login form
        if not data:
            return jsonify({'success': False, 'message': 'Invalid JSON payload'}), 400

        email = data.get('email')
        password = data.get('password')
        
        # Query the Doctor model by email
        doctor = Doctor.query.filter_by(email=email).first()
        if doctor and check_password_hash(doctor.hashed_password, password):
            # Store doctor ID (or other info) in session for persistence
            session['doctor'] = doctor.id
            return jsonify({'success': True, 'message': 'Doctor login successful!'})
        else:
            return jsonify({'success': False, 'message': 'Invalid email or password.'}), 401
    else:
        # For GET request, render the doctor login template
        return render_template('doctor_login.html')


@app.route('/doctor_dashboard', methods=['GET', 'POST'])
def doctor_dashboard():
    # Ensure the doctor is logged in
    if 'doctor' not in session:
        return redirect(url_for('doctor_login'))
    
    # Get the logged-in doctor's record
    doctor = Doctor.query.get(session['doctor'])
    if not doctor:
        session.pop('doctor', None)
        return redirect(url_for('doctor_login'))
    
    if request.method == 'POST':
        # Update doctor's details from the form submission
        doctor.name = request.form.get('name', doctor.name)
        # Typically email is not updated frequently, but if allowed:
        doctor.email = request.form.get('email', doctor.email)
        doctor.gender = request.form.get('gender', doctor.gender)
        try:
            doctor.experience = int(request.form.get('experience', doctor.experience))
        except ValueError:
            pass
        doctor.specialty = request.form.get('specialty', doctor.specialty)
        doctor.location = request.form.get('location', doctor.location)
        doctor.contact = request.form.get('contact', doctor.contact)

         # Update Aadhar Card Number
        doctor.aadhar_no = request.form.get('aadhar_no', doctor.aadhar_no)
        
        # Update password if new password is provided (optional update)
        new_password = request.form.get('new_password')
        if new_password:
            from werkzeug.security import generate_password_hash
            doctor.hashed_password = generate_password_hash(new_password)
        
        # Handle file updates (if new file is provided, update it)
        for field, folder in [('photo', 'photo'), ('degree_doc', 'degree'), ('aadhar_doc', 'aadhar')]:
            file = request.files.get(field)
            if file and allowed_file(file.filename):
                # Save the new file and update the field
                filename = save_file(file, folder)
                setattr(doctor, field, filename)
        
        try:
            db.session.commit()
            message = "Details updated successfully!"
        except Exception as e:
            db.session.rollback()
            message = f"Error updating details: {str(e)}"
        
        return render_template('doctor_dashboard.html', doctor=doctor, message=message)
    
    # For GET request, render the dashboard with current doctor details
    return render_template('doctor_dashboard.html', doctor=doctor)


# Doctor Registration Route
@app.route('/register_doctor', methods=['GET', 'POST'])
def register_doctor():
    if request.method == 'POST':
        # Handle form submission for doctor registration.
        # You can either process JSON or form data here.
        # For example, if using form data:
        required_fields = ['name', 'email', 'password', 'gender', 'experience', 
                           'specialty', 'location', 'contact', 'aadhar_no']
        data = {field: request.form.get(field) for field in required_fields}

        if not all(data.values()):
            return jsonify({"message": "All fields are required"}), 400

        try:
            data['experience'] = int(data['experience'])
        except ValueError:
            return jsonify({"message": "Experience must be a valid integer"}), 400

        if Doctor.query.filter_by(email=data['email']).first():
            return jsonify({"message": "Email already exists"}), 400
        if Doctor.query.filter_by(aadhar_no=data['aadhar_no']).first():
            return jsonify({"message": "Aadhar number already exists"}), 400

        uploaded_files = {
            'photo': request.files.get('photo'),
            'degree': request.files.get('degree_doc'),
            'aadhar': request.files.get('aadhar_doc')
        }
        for key, file in uploaded_files.items():
            if not file or not allowed_file(file.filename):
                return jsonify({"message": f"Invalid or missing {key} file"}), 400

        saved_files = {key: save_file(file, key) for key, file in uploaded_files.items()}

        new_doctor = Doctor(
            name=data['name'],  
            email=data['email'],
            hashed_password=generate_password_hash(data['password']),
            gender=data['gender'],
            experience=data['experience'],
            specialty=data['specialty'],
            location=data['location'],
            contact=data['contact'],
            aadhar_no=data['aadhar_no'],
            photo=saved_files['photo'],
            degree_doc=saved_files['degree'],
            aadhar_doc=saved_files['aadhar']
        )

        db.session.add(new_doctor)
        db.session.commit()
        return jsonify({"success":True,"message": "Doctor registered successfully!"}), 201

    # For GET request, simply render the doctor_registration template.
    return render_template('doctor_registration.html')

# ------------------------
# Main entry point
# ------------------------
if __name__ == '__main__':
    try:
        with app.app_context():
            db.create_all()
        print("Database connected successfully!")
    except Exception as e:
        print("Error connecting to database:", e)
    app.run(debug=True, host='0.0.0.0', port=5000)
