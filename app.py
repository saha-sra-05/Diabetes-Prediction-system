from flask import (

    Flask,
    render_template,
    request,
    redirect,
    session,
    send_file

)

from database import db

from werkzeug.security import (

    generate_password_hash,
    check_password_hash

)

import numpy as np
import joblib
import random

from datetime import datetime

from reportlab.platypus import (

    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle

)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from keras.models import Sequential
from keras.layers import Dense, Dropout, BatchNormalization

# ==========================================
# FLASK APP
# ==========================================

app = Flask(__name__)

app.secret_key = "diabetes_secret"

app.config[
    'SQLALCHEMY_DATABASE_URI'
] = 'sqlite:///users.db'

app.config[
    'SQLALCHEMY_TRACK_MODIFICATIONS'
] = False

db.init_app(app)

# ==========================================
# USER TABLE
# ==========================================

class User(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        unique=True
    )

    password = db.Column(
        db.String(200)
    )

# ==========================================
# PATIENT HISTORY TABLE
# ==========================================

class PatientHistory(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100)
    )

    patient_name = db.Column(
        db.String(100)
    )

    prediction = db.Column(
        db.String(100)
    )

    confidence = db.Column(
        db.Float
    )

    health_score = db.Column(
        db.Integer
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

# ==========================================
# MODEL ARCHITECTURE
# ==========================================

model = Sequential([

    Dense(
        64,
        activation='relu',
        input_shape=(8,)
    ),

    BatchNormalization(),

    Dropout(0.45),

    Dense(
        32,
        activation='relu'
    ),

    BatchNormalization(),

    Dropout(0.45),

    Dense(
        64,
        activation='relu'
    ),

    BatchNormalization(),

    Dropout(0.30),

    Dense(
        32,
        activation='relu'
    ),

    Dense(
        1,
        activation='sigmoid'
    )

])

# ==========================================
# LOAD WEIGHTS
# ==========================================

model.load_weights(
    'weights.weights.h5'
)

# ==========================================
# LOAD SCALER
# ==========================================

scaler = joblib.load(
    'scaler.pkl'
)

label_encoders = joblib.load(
    'label_encoders.pkl'
)

# ==========================================
# GLOBAL REPORT DATA
# ==========================================

report_data = {}

# ==========================================
# HOME
# ==========================================

@app.route('/')

def home():

    if 'user' not in session:

        return redirect('/login')

    return render_template(
        'index.html'
    )

# ==========================================
# SIGNUP
# ==========================================

@app.route(
    '/signup',
    methods=['GET','POST']
)

def signup():

    if request.method == 'POST':

        username = request.form['username']

        password = generate_password_hash(
            request.form['password']
        )

        user = User(

            username=username,

            password=password

        )

        db.session.add(user)

        db.session.commit()

        return redirect('/login')

    return render_template(
        'signup.html'
    )

# ==========================================
# LOGIN
# ==========================================

@app.route(
    '/login',
    methods=['GET','POST']
)

def login():

    if request.method == 'POST':

        username = request.form['username']

        password = request.form['password']

        user = User.query.filter_by(
            username=username
        ).first()

        if user and check_password_hash(

            user.password,
            password

        ):

            session['user'] = username

            return redirect('/')

    return render_template(
        'login.html'
    )

# ==========================================
# LOGOUT
# ==========================================

@app.route('/logout')

def logout():

    session.pop('user', None)

    return redirect('/login')

# ==========================================
# HISTORY PAGE
# ==========================================

@app.route('/history')

def history():

    if 'user' not in session:

        return redirect('/login')

    records = PatientHistory.query.filter_by(

        username=session['user']

    ).all()

    return render_template(

        'history.html',

        records=records

    )

# ==========================================
# PREDICTION
# ==========================================

@app.route(
    '/predict',
    methods=['POST']
)

def predict():

    global report_data

    try:

        # ==================================
        # INPUT VALUES
        # ==================================

        patient_name = request.form['patient_name']

        gender = request.form['gender']

        age = float(
            request.form['age']
        )

        bmi = float(
            request.form['bmi']
        )

        HbA1c_level = float(
            request.form['hba1c']
        )

        blood_glucose_level = float(
            request.form['glucose']
        )

        hypertension = int(
            request.form['hypertension']
        )

        heart_disease = int(
            request.form['heart_disease']
        )

        smoking_history = request.form[
            'smoking_history'
        ]

        # ==================================
        # ENCODING
        # ==================================

        gender_encoded = label_encoders[
            'gender'
        ].transform([gender])[0]

        smoking_encoded = label_encoders[
            'smoking_history'
        ].transform([smoking_history])[0]

        # ==================================
        # INPUT ARRAY
        # ==================================

        input_data = np.array([[

            gender_encoded,
            age,
            hypertension,
            heart_disease,
            smoking_encoded,
            bmi,
            HbA1c_level,
            blood_glucose_level

        ]])

        # ==================================
        # SCALE INPUT
        # ==================================

        input_scaled = scaler.transform(
            input_data
        )

        # ==================================
        # MODEL PREDICTION
        # ==================================

        prediction = model.predict(
            input_scaled
        )

        probability = float(
            prediction[0][0]
        )

        # ==================================
        # DIABETIC STATUS
        # ==================================

        if probability >= 0.5:

            diabetic_status = "DIABETIC"

        else:

            diabetic_status = "NON-DIABETIC"

        # ==================================
        # MEDICAL SAFETY RULE
        # ==================================

        if HbA1c_level >= 6.5 or blood_glucose_level >= 200:

            diabetic_status = "DIABETIC"

            probability = 0.95

        # ==================================
        # CONFIDENCE
        # ==================================

        confidence = round(
            probability * 100,
            2
        )

        # ==================================
        # RISK LEVEL
        # ==================================

        if probability < 0.30:

            risk = "LOW RISK"

            color = "#22c55e"

        elif probability < 0.60:

            risk = "MODERATE RISK"

            color = "#f59e0b"

        else:

            risk = "HIGH RISK"

            color = "#ef4444"

        # ==================================
        # HEALTH SCORE
        # ==================================

        health_score = int(
            (1 - probability) * 100
        )

        # ==================================
        # ALERTS
        # ==================================

        alerts = []

        if blood_glucose_level > 250:

            alerts.append(
                "Emergency glucose level detected."
            )

        if HbA1c_level > 9:

            alerts.append(
                "Critical HbA1c level detected."
            )

        # ==================================
        # ANALYSIS
        # ==================================

        analysis = []

        if blood_glucose_level > 180:

            analysis.append(
                "Blood glucose level is significantly elevated."
            )

        if HbA1c_level > 6.5:

            analysis.append(
                "HbA1c indicates elevated sugar levels."
            )

        if len(analysis) == 0:

            analysis.append(
                "Overall health indicators appear stable."
            )

        # ==================================
        # RECOMMENDATIONS
        # ==================================

        recommendations = [

            "Maintain healthy lifestyle.",

            "Exercise regularly.",

            "Avoid sugary foods.",

            "Drink enough water."

        ]

        # ==================================
        # DIET PLAN
        # ==================================

        diet_plan = [

            "Balanced healthy diet",

            "Fresh fruits and vegetables",

            "Avoid junk foods"

        ]

        # ==================================
        # EXERCISE PLAN
        # ==================================

        exercise_plan = [

            "Walking",

            "Jogging",

            "Yoga"

        ]

        # ==================================
        # FUTURE RISK
        # ==================================

        if probability > 0.6:

            future_risk = (
                "Future complications may increase."
            )

        else:

            future_risk = (
                "Current health indicators are manageable."
            )

        # ==================================
        # REPORT DETAILS
        # ==================================

        report_id = "REP" + str(
            random.randint(1000,9999)
        )

        report_date = datetime.now().strftime(
            "%d-%m-%Y %I:%M %p"
        )

        # ==================================
        # STORE REPORT DATA
        # ==================================

        report_data = {

            "patient_name": patient_name,
            "gender": gender,
            "age": age,
            "risk": risk,
            "confidence": confidence,
            "health_score": health_score,
            "analysis": analysis,
            "recommendations": recommendations,
            "report_id": report_id,
            "report_date": report_date,
            "bmi": bmi,
            "HbA1c_level": HbA1c_level,
            "blood_glucose_level": blood_glucose_level

        }

        # ==================================
        # SAVE HISTORY
        # ==================================

        history = PatientHistory(

            username=session['user'],

            patient_name=patient_name,

            prediction=diabetic_status,

            confidence=confidence,

            health_score=health_score

        )

        db.session.add(history)

        db.session.commit()

        # ==================================
        # RETURN PAGE
        # ==================================

        return render_template(

            'index.html',

            prediction=risk,

            diabetic_status=diabetic_status,

            confidence=confidence,

            health_score=health_score,

            analysis=analysis,

            recommendations=recommendations,

            alerts=alerts,

            diet_plan=diet_plan,

            exercise_plan=exercise_plan,

            future_risk=future_risk,

            bmi=round(bmi / 50, 2),

            HbA1c_level=round(HbA1c_level / 10, 2),

            blood_glucose_level=round(
                blood_glucose_level / 300,
                2
            ),

            color=color,

            report_id=report_id,

            report_date=report_date

        )

    except Exception as e:

        return render_template(

            'index.html',

            error=str(e)

        )

# ==========================================
# DOWNLOAD REPORT
# ==========================================

@app.route('/download_report')

def download_report():

    return send_file(

        "Medical_Report.pdf",

        as_attachment=True

    )

# ==========================================
# RUN APP
# ==========================================

with app.app_context():

    db.create_all()

if __name__ == '__main__':

    app.run(debug=True)
