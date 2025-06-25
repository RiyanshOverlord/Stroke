from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from app.models import User, Admin, Doctor
from app import db, mail, s  # `s` = URLSafeTimedSerializer from run.py

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def landing():
    return render_template('landing.html')

@auth_bp.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if 'username' in session:
        return redirect(url_for('prediction.chatbot'))
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
            if User.query.filter_by(email=email).first():
                return jsonify({'success': False, 'message': 'Email already registered.'}), 400

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


@auth_bp.route('/user_delete')
def user_delete():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized access'}), 401
    username = session['username']
    user = User.query.filter_by(username=username).first()
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
        user = User.query.filter_by(email=email).first()
        doctor = Doctor.query.filter_by(email=email).first()
        admin = Admin.query.filter_by(email=email).first()
        account = user or doctor or admin

        if account:
            token = s.dumps(email, salt='password-reset-salt')
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            name = getattr(account, 'username', None) or getattr(account, 'name', 'User')

            msg = Message(
                subject="Password Reset Request",
                recipients=[email],
                body=f"""
Hi {name},

You requested a password reset. Click the link below to reset your password:
{reset_url}

If you did not make this request, please ignore this email.

Regards,
Your App Team
""")
            mail.send(msg)
            return render_template('forgot_password.html', message="A password reset link has been sent to your email.")
        else:
            return render_template('forgot_password.html', message="Email not found.")
    return render_template('forgot_password.html')


@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=3600)
    except SignatureExpired:
        return "The reset link has expired.", 400
    except BadSignature:
        return "Invalid reset token.", 400

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
        return redirect(url_for('auth.landing'))

    return render_template('reset_password.html', token=token)
