from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import os
import pandas as pd
import joblib
import logging
from flask_login import LoginManager, UserMixin, current_user, login_user, login_required, logout_user
from flask_migrate import Migrate

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default_fallback_secret_key')

login_manager = LoginManager()
login_manager.init_app(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:moonsoul@localhost:3307/loan_approval'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# Load the model and scaler
try:
    model = joblib.load('model/loan_model.pkl')
    scaler = joblib.load('model/scaler.pkl')
except Exception as e:
    logging.error(f"Error loading model or scaler: {e}")
    raise

# Models
class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    account_no = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Simulated plain password storage
    def set_password(self, password):
        self.password_hash = password

    def check_password(self, password):
        return self.password_hash == password

class Application(db.Model):
    application_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    loan_amount = db.Column(db.Float)
    loan_term = db.Column(db.Integer)
    application_status = db.Column(db.Enum('Submitted', 'Under Review', 'Approved', 'Rejected'), default='Submitted')
    prediction_result = db.Column(db.Boolean)
    submission_date = db.Column(db.DateTime, default=db.func.current_timestamp())

class Officer(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    
    def set_password(self, password):
        self.password_hash = password  # Store plain text password directly

    def check_password(self, password):
        return self.password_hash == password  # Compare plain text passwords
   
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) or Officer.query.get(int(user_id))

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/check_loan')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        account_no = request.form['account_no']
        password = request.form['password']
        
        user = User.query.filter_by(account_no=account_no).first()
        if user and user.check_password(password):
            session['user_id'] = user.user_id
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')

    return render_template('login.html')

@app.route('/officer_login', methods=['GET', 'POST'])
def officer_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        officer = Officer.query.filter_by(username=username).first()
        if officer and officer.check_password(password):
            login_user(officer)
            flash('Officer login successful!', 'success')
            return redirect(url_for('officer_dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')

    return render_template('officer_login.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = {
        'no_of_dependents': int(request.form['no_of_dependents']),
        'education': request.form['education'],
        'self_employed': request.form['self_employed'],
        'income_annum': float(request.form['income_annum']),
        'loan_amount': float(request.form['loan_amount']),
        'loan_term': int(request.form['loan_term']),
        'cibil_score': float(request.form['cibil_score']),
        'residential_assets_value': float(request.form['residential_assets_value']),
        'commercial_assets_value': float(request.form['commercial_assets_value']),
        'luxury_assets_value': float(request.form['luxury_assets_value']),
        'bank_asset_value': float(request.form['bank_asset_value'])
    }

    df = pd.DataFrame([data])
    df['education'] = df['education'].map({'Graduate': 1, 'Not Graduate': 0})
    df['self_employed'] = df['self_employed'].map({'Yes': 1, 'No': 0})
    
    df_scaled = scaler.transform(df)
    prediction = model.predict(df_scaled)[0]

    if prediction == 1:
        flash('Congratulations! You have a high chance of loan approval.', 'success')
        prediction_result = True
    else:
        flash('Unfortunately, your loan application might not be approved.', 'warning')
        prediction_result = False

    return render_template('result.html', prediction_result=prediction_result)

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = current_user.id
    applications = Application.query.filter_by(user_id=user_id).all()
    return render_template('dashboard.html', applications=applications)

@app.route('/submit_application', methods=['POST'])
@login_required
def submit_application():
    try:
        loan_amount = float(request.form.get('loan_amount', '0'))
        loan_term = int(request.form.get('loan_term', '0'))
        prediction_result = request.form.get('prediction_result', 'false') == 'true'

        application = Application(
            user_id=current_user.id,
            loan_amount=loan_amount,
            loan_term=loan_term,
            application_status='Submitted',
            prediction_result=prediction_result
        )

        db.session.add(application)
        db.session.commit()

        flash('Application submitted successfully!', 'success')
    except ValueError as e:
        logging.error(f"ValueError: {e}")
        flash('Invalid data provided. Please check your inputs and try again.', 'danger')
    except Exception as e:
        logging.error(f"Error during application submission: {e}")
        flash('An error occurred while submitting your application. Please try again later.', 'danger')

    return redirect(url_for('dashboard'))

@app.route('/application_status/<int:application_id>')
@login_required
def application_status(application_id):
    application = Application.query.get_or_404(application_id)

    if application.user_id != current_user.id:
        flash('You are not authorized to view this application.', 'danger')
        return redirect(url_for('dashboard'))

    return render_template('application_status.html', application=application)



@app.route('/officer_dashboard')
@login_required
def officer_dashboard():
    if not isinstance(current_user, Officer):
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))

    applications = Application.query.all()
    return render_template('officer_dashboard.html', applications=applications)

@app.route('/review_application/<int:application_id>', methods=['GET', 'POST'])
@login_required
def review_application(application_id):
    if not isinstance(current_user, Officer):
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))

    application = Application.query.get_or_404(application_id)

    if request.method == 'POST':
        status = request.form.get('status')
        if status in ['Under Review', 'Approved', 'Rejected']:
            application.application_status = status
            db.session.commit()
            flash('Application status updated successfully!', 'success')
            return redirect(url_for('officer_dashboard'))

    return render_template('review_application.html', application=application)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/test_redirect')
def test_redirect():
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
