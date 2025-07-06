from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify, send_from_directory
import pandas as pd
from app.models import Hospital, Doctor
from app.utils.model_utils import load_model_components,train_and_save_model
from app.utils.file_utils import get_folders
import os

prediction_bp = Blueprint('prediction', __name__)

#  Train model once during startup
csv_path = os.getenv('CSV_PATH')
if not all(os.path.exists(os.path.exists(os.path.join('models', f))) for f in ['model.pkl', 'scaler.pkl', 'features.pkl']):
    print("Model Trained AGAIN")
    train_and_save_model(csv_path)
best_model, scaler, selected_features = load_model_components()
@prediction_bp.route('/chatbot')
def chatbot():
    if 'username' in session:
        return render_template('chatbot.html', username=session['username'])
    session.clear()
    return redirect(url_for('auth.user_login'))


@prediction_bp.route('/submit_chatbot', methods=['POST'])
def submit_chatbot():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON payload'}), 400

    try:
        height_cm = float(data.get('What is your height in centimeters ?', 0))
        weight_kg = float(data.get('What is your weight in kilograms ?', 0))
        bmi = weight_kg / ((height_cm / 100.0) ** 2) if height_cm > 0 and weight_kg > 0 else 24.5
    except Exception:
        bmi = 24.5

    session['chatbot_data'] = data
    session['bmi'] = bmi

    return jsonify({'success': True, 'message': 'Chatbot data received', 'bmi': bmi})


@prediction_bp.route('/report')
def report():
    if 'username' not in session:
        return redirect(url_for('auth.user_login'))

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
    risk_label = "High Risk" if prob >= 0.55 else "Low/Moderate Risk"

    hospitals = Hospital.query.all()
    hospitals_result = [{
        "id": h.id,
        "name": h.hospital,
        "state": h.state,
        "city": h.city,
        "address": h.local_address,
        "pincode": h.pincode
    } for h in hospitals]

    doctors = Doctor.query.all()
    doctors_result = [{
        "name": d.name,
        "email": d.email,
        "gender": d.gender,
        "experience": d.experience,
        "specialty": d.specialty,
        "contact": d.contact,
        "location": d.location
    } for d in doctors]

    return render_template('report.html',
                           bmi=round(bmi, 2),
                           user_prediction_label=risk_label,
                           user_prediction_percentage=user_prediction_percentage,
                           hospitals=hospitals_result,
                           doctors=doctors_result)


@prediction_bp.route('/filter/hospitals', methods=['GET'])
def filter_hospitals():
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


@prediction_bp.route('/filter/doctors', methods=['GET'])
def filter_doctors():
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
        "specialty": d.specialty,
        "contact": d.contact,
        "location": d.location
    } for d in doctors]
    return jsonify(result)


@prediction_bp.route('/uploads/<folder>/<filename>')
def serve_file(folder, filename):
    folders = get_folders()
    if folder not in folders:
        return jsonify({"message": "Invalid folder!"}), 403
    return  send_from_directory(get_folders()[folder], filename)