from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User, Admin, Doctor
from app import db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin_register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Invalid JSON payload'}), 400
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        hashed_password = generate_password_hash(password)
        if Admin.query.filter((Admin.username == username) | (Admin.email == email)).first():
            return jsonify({'success': False, 'message': 'Admin already exists.'}), 400
        db.session.add(Admin(username=username, email=email, hashed_password=hashed_password))
        db.session.commit()
        return jsonify({'success': True, 'message': 'Admin registration successful!'})
    return render_template('admin_register.html')

@admin_bp.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if 'admin' in session:
        return redirect(url_for('admin.admin_dashboard'))
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
        return jsonify({'success': False, 'message': 'Invalid email or password.'}), 401
    return render_template('admin_login.html')

@admin_bp.route('/admin_dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin.admin_login'))
    users = User.query.all()
    doctors = Doctor.query.all()
    return render_template('admin_dashboard.html', users=users, doctors=doctors)

@admin_bp.route('/delete_user/<int:user_id>', methods=['DELETE'])
def delete_user_by_admin(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'success': True, 'message': 'User deleted successfully!'})
    return jsonify({'success': False, 'message': 'User not found.'}), 404

@admin_bp.route('/delete_doctor/<int:doctor_id>', methods=['DELETE'])
def delete_doctor_by_admin(doctor_id):
    doctor = Doctor.query.get(doctor_id)
    if doctor:
        db.session.delete(doctor)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Doctor deleted successfully!'})
    return jsonify({'success': False, 'message': 'Doctor not found.'}), 404
