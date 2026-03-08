from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(200))

class Violation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_number = db.Column(db.String(20))
    violation_type = db.Column(db.String(100))
    location = db.Column(db.String(100))
    date = db.Column(db.String(20))
    fine_amount = db.Column(db.Integer)
    payment_status = db.Column(db.String(20), default="Unpaid")
    tamper_status = db.Column(db.String(20))
    qr_code = db.Column(db.String(200))