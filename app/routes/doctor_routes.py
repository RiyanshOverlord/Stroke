from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import Doctor
from app.utils.file_utils import allowed_file, save_file
from app import db

doctor_bp = Blueprint('doctor', __name__)

@doctor_bp.route('/doctor_login', methods=['GET', 'POST'])
def doctor_login():
    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Invalid JSON payload'}), 400

        email = data.get('email')
        password = data.get('password')
        doctor = Doctor.query.filter_by(email=email).first()
        if doctor and check_password_hash(doctor.hashed_password, password):
            session['doctor'] = doctor.id
            return jsonify({'success': True, 'message': 'Doctor login successful!'})
        else:
            return jsonify({'success': False, 'message': 'Invalid email or password.'}), 401

    return render_template('doctor_login.html')


@doctor_bp.route('/doctor_dashboard', methods=['GET', 'POST'])
def doctor_dashboard():
    if 'doctor' not in session:
        return redirect(url_for('doctor.doctor_login'))

    doctor = Doctor.query.get(session['doctor'])
    if not doctor:
        session.pop('doctor', None)
        return redirect(url_for('doctor.doctor_login'))

    if request.method == 'POST':
        doctor.name = request.form.get('name', doctor.name)
        doctor.email = request.form.get('email', doctor.email)
        doctor.gender = request.form.get('gender', doctor.gender)
        try:
            doctor.experience = int(request.form.get('experience', doctor.experience))
        except ValueError:
            pass
        doctor.specialty = request.form.get('specialty', doctor.specialty)
        doctor.location = request.form.get('location', doctor.location)
        doctor.contact = request.form.get('contact', doctor.contact)
        doctor.aadhar_no = request.form.get('aadhar_no', doctor.aadhar_no)

        new_password = request.form.get('new_password')
        if new_password:
            doctor.hashed_password = generate_password_hash(new_password)

        for field, folder in [('photo', 'photo'), ('degree_doc', 'degree'), ('aadhar_doc', 'aadhar')]:
            file = request.files.get(field)
            if file and allowed_file(file.filename):
                filename = save_file(file, folder)
                setattr(doctor, field, filename)

        try:
            db.session.commit()
            message = "Details updated successfully!"
        except Exception as e:
            db.session.rollback()
            message = f"Error updating details: {str(e)}"

        return render_template('doctor_dashboard.html', doctor=doctor, message=message)

    return render_template('doctor_dashboard.html', doctor=doctor)


@doctor_bp.route('/register_doctor', methods=['GET', 'POST'])
def register_doctor():
    if request.method == 'POST':
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
        return jsonify({"success": True, "message": "Doctor registered successfully!"}), 201

    return render_template('doctor_registration.html')

