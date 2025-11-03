from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import sqlite3
import json
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'patient_login'

DATABASE = 'therapy.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''CREATE TABLE IF NOT EXISTS patients
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       name TEXT NOT NULL,
                       email TEXT UNIQUE NOT NULL,
                       phone TEXT,
                       password_hash TEXT NOT NULL,
                       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        db.execute('''CREATE TABLE IF NOT EXISTS appointments
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       patient_name TEXT NOT NULL,
                       patient_email TEXT NOT NULL,
                       patient_phone TEXT NOT NULL,
                       appointment_date TEXT NOT NULL,
                       appointment_time TEXT NOT NULL,
                       status TEXT DEFAULT 'scheduled',
                       patient_id INTEGER,
                       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                       FOREIGN KEY (patient_id) REFERENCES patients (id))''')
        
        db.execute('''CREATE TABLE IF NOT EXISTS session_notes
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       appointment_id INTEGER NOT NULL,
                       patient_id INTEGER NOT NULL,
                       notes TEXT NOT NULL,
                       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                       FOREIGN KEY (appointment_id) REFERENCES appointments (id),
                       FOREIGN KEY (patient_id) REFERENCES patients (id))''')
        
        db.execute('''CREATE TABLE IF NOT EXISTS magazines
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       title_en TEXT NOT NULL,
                       title_uz TEXT NOT NULL,
                       title_ru TEXT NOT NULL,
                       description_en TEXT,
                       description_uz TEXT,
                       description_ru TEXT,
                       link TEXT,
                       type TEXT NOT NULL,
                       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        count = db.execute("SELECT COUNT(*) as count FROM magazines").fetchone()['count']
        if count == 0:
            sample_content = [
                ('Understanding Body-Mind Connection', 'Tana va Aql Aloqasini Tushunish', 'Понимание Связи Тела и Разума', 
                 'Exploring the relationship between physical sensations and emotional states', 
                 'Jismoniy his-tuyg\'ular va hissiy holatlar o\'rtasidagi munosabatlarni o\'rganish',
                 'Изучение взаимосвязи между физическими ощущениями и эмоциональными состояниями',
                 '#', 'magazine'),
                ('Healthy Relationships Workshop', 'Sog\'lom Munosabatlar Seminari', 'Семинар Здоровых Отношений',
                 'Building strong and meaningful connections with others',
                 'Boshqalar bilan mustahkam va ma\'noli aloqalar o\'rnatish',
                 'Построение крепких и значимых связей с другими',
                 '#', 'podcast'),
                ('Personal Growth Journey', 'Shaxsiy O\'sish Sayohati', 'Путь Личностного Роста',
                 'Steps towards self-discovery and transformation',
                 'O\'zini kashf qilish va o\'zgarish tomon qadamlar',
                 'Шаги к самопознанию и трансформации',
                 '#', 'magazine')
            ]
            for content in sample_content:
                db.execute('''INSERT INTO magazines (title_en, title_uz, title_ru, description_en, description_uz, description_ru, link, type)
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', content)
        
        db.commit()
        db.close()

class User(UserMixin):
    def __init__(self, id, email, name, is_doctor=False):
        self.id = id
        self.email = email
        self.name = name
        self.is_doctor = is_doctor

@login_manager.user_loader
def load_user(user_id):
    if user_id.startswith('doctor_'):
        return User('doctor_admin', 'doctor@admin.com', 'Dr. Guli', is_doctor=True)
    
    db = get_db()
    patient = db.execute('SELECT * FROM patients WHERE id = ?', (user_id,)).fetchone()
    db.close()
    
    if patient:
        return User(patient['id'], patient['email'], patient['name'])
    return None

@app.route('/')
def index():
    lang = request.args.get('lang', session.get('language', 'en'))
    session['language'] = lang
    return render_template('index.html', lang=lang)

@app.route('/about')
def about():
    lang = request.args.get('lang', session.get('language', 'en'))
    session['language'] = lang
    return render_template('about.html', lang=lang)

@app.route('/appointment', methods=['GET', 'POST'])
def appointment():
    lang = request.args.get('lang', session.get('language', 'en'))
    session['language'] = lang
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        date = request.form.get('date')
        time = request.form.get('time')
        
        db = get_db()
        patient = db.execute('SELECT * FROM patients WHERE email = ?', (email,)).fetchone()
        patient_id = patient['id'] if patient else None
        
        db.execute('''INSERT INTO appointments (patient_name, patient_email, patient_phone, appointment_date, appointment_time, patient_id)
                     VALUES (?, ?, ?, ?, ?, ?)''', (name, email, phone, date, time, patient_id))
        db.commit()
        db.close()
        
        flash('Appointment booked successfully!', 'success')
        return redirect(url_for('appointment', lang=lang))
    
    return render_template('appointment.html', lang=lang)

@app.route('/patient/login', methods=['GET', 'POST'])
def patient_login():
    lang = request.args.get('lang', session.get('language', 'en'))
    session['language'] = lang
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'register':
            name = request.form.get('name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            password = request.form.get('password')
            
            db = get_db()
            existing = db.execute('SELECT * FROM patients WHERE email = ?', (email,)).fetchone()
            
            if existing:
                flash('Email already registered!', 'error')
                db.close()
                return redirect(url_for('patient_login', lang=lang))
            
            password_hash = generate_password_hash(password)
            db.execute('INSERT INTO patients (name, email, phone, password_hash) VALUES (?, ?, ?, ?)',
                      (name, email, phone, password_hash))
            db.commit()
            db.close()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('patient_login', lang=lang))
        
        elif action == 'login':
            email = request.form.get('email')
            password = request.form.get('password')
            
            db = get_db()
            patient = db.execute('SELECT * FROM patients WHERE email = ?', (email,)).fetchone()
            db.close()
            
            if patient and check_password_hash(patient['password_hash'], password):
                user = User(patient['id'], patient['email'], patient['name'])
                login_user(user)
                return redirect(url_for('patient_dashboard', lang=lang))
            else:
                flash('Invalid credentials!', 'error')
    
    return render_template('patient_login.html', lang=lang)

@app.route('/patient/dashboard')
@login_required
def patient_dashboard():
    if current_user.is_doctor:
        return redirect(url_for('doctor_dashboard'))
    
    lang = request.args.get('lang', session.get('language', 'en'))
    session['language'] = lang
    
    db = get_db()
    appointments = db.execute('''SELECT a.*, sn.notes 
                                FROM appointments a 
                                LEFT JOIN session_notes sn ON a.id = sn.appointment_id
                                WHERE a.patient_id = ? 
                                ORDER BY a.appointment_date DESC, a.appointment_time DESC''', 
                             (current_user.id,)).fetchall()
    db.close()
    
    return render_template('patient_dashboard.html', appointments=appointments, lang=lang)

@app.route('/patient/logout')
@login_required
def patient_logout():
    lang = session.get('language', 'en')
    logout_user()
    return redirect(url_for('index', lang=lang))

@app.route('/doctor/login', methods=['GET', 'POST'])
def doctor_login():
    lang = request.args.get('lang', session.get('language', 'en'))
    session['language'] = lang
    
    if request.method == 'POST':
        password = request.form.get('password')
        
        if password == 'DrGuli2024':
            user = User('doctor_admin', 'doctor@admin.com', 'Dr. Guli', is_doctor=True)
            login_user(user)
            return redirect(url_for('doctor_dashboard', lang=lang))
        else:
            flash('Invalid password!', 'error')
    
    return render_template('doctor_login.html', lang=lang)

@app.route('/doctor/dashboard')
@login_required
def doctor_dashboard():
    if not current_user.is_doctor:
        return redirect(url_for('patient_dashboard'))
    
    lang = request.args.get('lang', session.get('language', 'en'))
    session['language'] = lang
    
    db = get_db()
    appointments = db.execute('''SELECT a.*, p.name as patient_registered_name, sn.notes, sn.id as note_id
                                FROM appointments a 
                                LEFT JOIN patients p ON a.patient_id = p.id
                                LEFT JOIN session_notes sn ON a.id = sn.appointment_id
                                ORDER BY a.appointment_date DESC, a.appointment_time DESC''').fetchall()
    
    patients = db.execute('SELECT * FROM patients ORDER BY created_at DESC').fetchall()
    db.close()
    
    return render_template('doctor_dashboard.html', appointments=appointments, patients=patients, lang=lang)

@app.route('/doctor/add-note/<int:appointment_id>', methods=['POST'])
@login_required
def add_note(appointment_id):
    if not current_user.is_doctor:
        return redirect(url_for('index'))
    
    lang = session.get('language', 'en')
    notes = request.form.get('notes')
    
    db = get_db()
    appointment = db.execute('SELECT * FROM appointments WHERE id = ?', (appointment_id,)).fetchone()
    
    if appointment and appointment['patient_id']:
        existing_note = db.execute('SELECT * FROM session_notes WHERE appointment_id = ?', (appointment_id,)).fetchone()
        
        if existing_note:
            db.execute('UPDATE session_notes SET notes = ? WHERE appointment_id = ?', (notes, appointment_id))
        else:
            db.execute('INSERT INTO session_notes (appointment_id, patient_id, notes) VALUES (?, ?, ?)',
                      (appointment_id, appointment['patient_id'], notes))
        db.commit()
        flash('Session notes saved successfully!', 'success')
    else:
        flash('Cannot add notes for unregistered patients!', 'error')
    
    db.close()
    return redirect(url_for('doctor_dashboard', lang=lang))

@app.route('/doctor/logout')
@login_required
def doctor_logout():
    lang = session.get('language', 'en')
    logout_user()
    return redirect(url_for('index', lang=lang))

@app.route('/media')
def media():
    lang = request.args.get('lang', session.get('language', 'en'))
    session['language'] = lang
    
    db = get_db()
    content = db.execute('SELECT * FROM magazines ORDER BY created_at DESC').fetchall()
    db.close()
    
    return render_template('media.html', content=content, lang=lang)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
