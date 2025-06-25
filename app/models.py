from . import db
from datetime import datetime, timezone

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    date_created = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    hashed_password = db.Column(db.Text, nullable=False)

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

class Hospital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hospital = db.Column(db.String(100), nullable=False)
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