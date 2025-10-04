from flask import Flask, render_template, request, redirect, url_for, session, flash
import pandas as pd
import joblib
import os
import json
from flask_mail import Mail, Message

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
os.makedirs(STATIC_DIR, exist_ok=True)

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'your_secret_key'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'bordepratik32@gmail.com'
app.config['MAIL_PASSWORD'] = 'ktczlrnczymijiyw'  
app.config['MAIL_DEFAULT_SENDER'] = 'bordepratik32@gmail.com'

mail = Mail(app)

MODEL_PATH = os.path.join(BASE_DIR, "model", "ids_rf_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "model", "scaler.pkl")
ENCODERS_PATH = os.path.join(BASE_DIR, "model", "label_encoders.pkl")

model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)
label_encoders = joblib.load(ENCODERS_PATH)

USERS_FILE = os.path.join(BASE_DIR, 'users.json')
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'w') as f:
        json.dump({}, f)

def get_user_email(username):
    try:
        with open(USERS_FILE, 'r') as f:
            users = json.load(f)
            return users.get(username, {}).get('email', '')
    except:
        return ''

@app.context_processor
def inject_user_email():
    return dict(get_user_email=get_user_email)

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        if 'user' not in session:
            flash('You must be logged in to send a message.', 'error')
            return redirect(url_for('login'))

        name = session.get('user')
        email = get_user_email(name)
        message = request.form.get('message')

        if not message:
            flash('Message cannot be empty.', 'error')
            return redirect(url_for('contact'))

        try:
            msg = Message(subject=f"📩 Message from {name}",
                          sender=app.config['MAIL_USERNAME'],
                          recipients=[app.config['MAIL_USERNAME']],
                          body=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}")
            mail.send(msg)
            flash('Your message was sent successfully!', 'success')
        except Exception as e:
            print(f"❌ Email failed: {e}")
            flash('Failed to send your message. Try again later.', 'error')

        return redirect(url_for('contact'))

    return render_template('contact.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm_password']

        if password != confirm:
            return render_template('register.html', error="Passwords do not match.")

        with open(USERS_FILE, 'r') as f:
            try:
                users = json.load(f)
            except:
                users = {}

        if username in users:
            return render_template('register.html', error="User already exists.")

        users[username] = {"email": email, "password": password}
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f, indent=4)

        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with open(USERS_FILE, 'r') as f:
            try:
                users = json.load(f)
            except:
                users = {}

        if username in users and users[username]['password'] == password:
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid credentials.")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        file = request.files.get('file')
        if file and file.filename.lower().endswith('.csv'):
            try:
                df = pd.read_csv(file)

                for col in ['protocol_type', 'service', 'flag']:
                    if col in df.columns and col in label_encoders:
                        df[col] = label_encoders[col].transform(df[col])

                for col in df.select_dtypes(include=['object']).columns:
                    df[col] = df[col].astype('category').cat.codes

                df.drop(columns=['label'], errors='ignore', inplace=True)

                X_scaled = scaler.transform(df)
                predictions = model.predict(X_scaled)

                df['Prediction'] = ['Normal' if p == 0 else 'Attack' for p in predictions]
                display_df = df[list(df.columns[:5]) + ['Prediction']]

                output_path = os.path.join(STATIC_DIR, 'predicted_output.csv')
                df.to_csv(output_path, index=False)

                return render_template('result.html',
                                       tables=[display_df.to_html(classes='table table-bordered', index=False)],
                                       download_link=url_for('static', filename='predicted_output.csv'))
            except Exception as e:
                return render_template('dashboard.html', error=f"Error processing file: {str(e)}")

        return render_template('dashboard.html', error="Please upload a valid CSV file.")

    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
