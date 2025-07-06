from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from app.models import User, Admin, Doctor
from app import db, mail
from app.utils.email_utils import get_serializer,generate_token,verify_token,send_reset_email

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def landing():
    return render_template('landing.html')

@auth_bp.route('/info')
def info():
    return render_template('info.html')

@auth_bp.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if 'username' in session:
        return redirect(url_for('prediction.chatbot'))

    if request.method == 'POST':
        try:
            data = request.get_json(force=True)
            if not data:
                return jsonify({'success': False, 'message': 'Invalid JSON payload'}), 400

            form_type = data.get('form_type')
            if form_type == "register":
                username = data.get('username')
                email = data.get('email')
                password = data.get('password')

                if not all([username, email, password]):
                    return jsonify({'success': False, 'message': 'Missing registration fields.'}), 400

                if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
                    return jsonify({'success': False, 'message': 'User already exists.'}), 400

                hashed_password = generate_password_hash(password)
                db.session.add(User(username=username, email=email, hashed_password=hashed_password))
                db.session.commit()
                return jsonify({'success': True, 'message': 'Registration successful!'})

            elif form_type == "login":
                email = data.get('email')
                password = data.get('password')

                if not email or not password:
                    return jsonify({'success': False, 'message': 'Missing login fields.'}), 400

                found_user = User.query.filter_by(email=email).first()
                if found_user and check_password_hash(found_user.hashed_password, password):
                    session['username'] = found_user.username
                    return jsonify({'success': True, 'message': 'Login successful!'})
                return jsonify({'success': False, 'message': 'Invalid email or password.'}), 401

            return jsonify({'success': False, 'message': 'Unknown form type.'}), 400

        except Exception as e:
            print(" Login/Registration Error:", e)
            return jsonify({'success': False, 'message': 'Server error occurred.'}), 500

    return render_template('index.html')


@auth_bp.route('/user_delete')
def user_delete():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized access'}), 401
    user = User.query.filter_by(username=session['username']).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        session.clear()
        return jsonify({'success': True, 'message': 'User deleted successfully!'})
    return redirect(url_for('auth.clear_session'))

@auth_bp.route('/clear_session')
def clear_session():
    session.clear()
    return redirect(url_for('auth.user_login'))

@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        account = User.query.filter_by(email=email).first() or \
                  Doctor.query.filter_by(email=email).first() or \
                  Admin.query.filter_by(email=email).first()
        if account:
            token = generate_token(email)
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            name = getattr(account, 'username', None) or getattr(account, 'name', 'User')
            
            send_reset_email(email, name, reset_url)

            return render_template('forgot_password.html', message="A reset link has been sent.")
        return render_template('forgot_password.html', message="Email not found.")
    return render_template('forgot_password.html')


@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = verify_token(token)
    if not email:
        return "Invalid or expired token", 400

    account = User.query.filter_by(email=email).first() or \
              Doctor.query.filter_by(email=email).first() or \
              Admin.query.filter_by(email=email).first()

    if not account:
        return "User not found.", 404

    if request.method == 'POST':
        new_password = request.form.get('password')
        if not new_password or len(new_password) < 8:
            return render_template('reset_password.html', token=token, message="Password must be at least 8 characters.")
        account.hashed_password = generate_password_hash(new_password)
        db.session.commit()
        return redirect(url_for('auth.user_login'))
    
    return render_template('reset_password.html', token=token)
