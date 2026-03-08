from flask import Flask, render_template, request, redirect, url_for
from models import db, User, Violation
from flask_login import LoginManager, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import qrcode
from tamper_detection import detect_tampering

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///traffic.db'

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def home():
    return redirect('/login')


# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect('/dashboard')
    return render_template('login.html')


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


# ---------------- ADD VIOLATION ----------------
@app.route('/add', methods=['GET','POST'])
@login_required
def add_violation():

    if request.method == 'POST':
        file = request.files['plate_image']
        image_path = os.path.join('static/uploads', file.filename)
        file.save(image_path)

        tamper_status, plate_number = detect_tampering(image_path)

        violation = Violation(
            vehicle_number=plate_number,
            violation_type=request.form['violation_type'],
            location=request.form['location'],
            date=request.form['date'],
            fine_amount=request.form['fine'],
            tamper_status=tamper_status
        )

        db.session.add(violation)
        db.session.commit()

        # QR Generation
        qr = qrcode.make(f"http://127.0.0.1:5000/status/{violation.id}")
        qr_path = f"static/qr_codes/{violation.id}.png"
        qr.save(qr_path)

        violation.qr_code = qr_path
        db.session.commit()

        return render_template("result.html", violation=violation)

    return render_template('add_violation.html')


# ---------------- HISTORY ----------------
@app.route('/history')
@login_required
def history():
    vehicle = request.args.get('vehicle')
    if vehicle:
        records = Violation.query.filter_by(vehicle_number=vehicle).all()
    else:
        records = Violation.query.all()

    return render_template('history.html', records=records)


# ---------------- UPDATE STATUS ----------------
@app.route('/pay/<int:id>')
@login_required
def mark_paid(id):
    violation = Violation.query.get(id)
    violation.payment_status = "Paid"
    db.session.commit()
    return redirect('/history')


# ---------------- PUBLIC STATUS ----------------
@app.route('/status/<int:id>')
def public_status(id):
    violation = Violation.query.get(id)
    return render_template('public_status.html', violation=violation)


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/login')


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)