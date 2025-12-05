from flask import Flask, render_template, request, redirect, url_for, flash, session, g
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "SESSION_SECRET", "dev-secret-key-change-in-production"
)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "patient_login"
login_manager.login_message_category = "info"

DATABASE = "therapy.db"
DOCTOR_PASSWORD = os.environ.get("DOCTOR_PASSWORD", "DrGuli2024")


# ---------- DATABASE HELPERS ----------


def get_db():
    """Get a SQLite connection for the current request."""
    if "db" not in g:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        # Enforce foreign key constraints in SQLite
        conn.execute("PRAGMA foreign_keys = ON")
        g.db = conn
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    """Close the database at the end of the request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create tables and seed initial data if needed."""
    with app.app_context():
        db = get_db()

        db.execute(
            """CREATE TABLE IF NOT EXISTS patients
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       name TEXT NOT NULL,
                       email TEXT UNIQUE NOT NULL,
                       phone TEXT,
                       password_hash TEXT NOT NULL,
                       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"""
        )

        db.execute(
            """CREATE TABLE IF NOT EXISTS appointments
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       patient_name TEXT NOT NULL,
                       patient_email TEXT NOT NULL,
                       patient_phone TEXT NOT NULL,
                       appointment_date TEXT NOT NULL,
                       appointment_time TEXT NOT NULL,
                       status TEXT DEFAULT 'scheduled',
                       patient_id INTEGER,
                       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                       FOREIGN KEY (patient_id) REFERENCES patients (id))"""
        )

        db.execute(
            """CREATE TABLE IF NOT EXISTS session_notes
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       appointment_id INTEGER NOT NULL,
                       patient_id INTEGER NOT NULL,
                       notes TEXT NOT NULL,
                       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                       FOREIGN KEY (appointment_id) REFERENCES appointments (id),
                       FOREIGN KEY (patient_id) REFERENCES patients (id))"""
        )

        db.execute(
            """CREATE TABLE IF NOT EXISTS magazines
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       title_en TEXT NOT NULL,
                       title_uz TEXT NOT NULL,
                       title_ru TEXT NOT NULL,
                       description_en TEXT,
                       description_uz TEXT,
                       description_ru TEXT,
                       link TEXT,
                       type TEXT NOT NULL,
                       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"""
        )

        count = db.execute(
            "SELECT COUNT(*) as count FROM magazines"
        ).fetchone()["count"]
        if count == 0:
            sample_content = [
                (
                    "Understanding Body-Mind Connection",
                    "Tana va Aql Aloqasini Tushunish",
                    "Понимание Связи Тела и Разума",
                    "Exploring the relationship between physical sensations and emotional states",
                    "Jismoniy his-tuyg'ular va hissiy holatlar o'rtasidagi munosabatlarni o'rganish",
                    "Изучение взаимосвязи между физическими ощущениями и эмоциональными состояниями",
                    "#",
                    "magazine",
                ),
                (
                    "Healthy Relationships Workshop",
                    "Sog'lom Munosabatlar Seminari",
                    "Семинар Здоровых Отношений",
                    "Building strong and meaningful connections with others",
                    "Boshqalar bilan mustahkam va ma'noli aloqalar o'rnatish",
                    "Построение крепких и значимых связей с другими",
                    "#",
                    "podcast",
                ),
                (
                    "Personal Growth Journey",
                    "Shaxsiy O'sish Sayohati",
                    "Путь Личностного Роста",
                    "Steps towards self-discovery and transformation",
                    "O'zini kashf qilish va o'zgarish tomon qadamlar",
                    "Шаги к самопознанию и трансформации",
                    "#",
                    "magazine",
                ),
            ]
            for content in sample_content:
                db.execute(
                    """INSERT INTO magazines
                       (title_en, title_uz, title_ru, description_en, description_uz,
                        description_ru, link, type)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    content,
                )

        db.commit()
# Make sure the DB is initialized on the server (Render / gunicorn)
@app.before_request
def initialize_database():
    init_db()


# ---------- USER MODEL & LOGIN ----------


class User(UserMixin):
    def __init__(self, id, email, name, is_doctor=False):
        self.id = id
        self.email = email
        self.name = name
        self.is_doctor = is_doctor


@login_manager.user_loader
def load_user(user_id):
    """Reload user from the session."""
    if not user_id:
        return None

    user_id = str(user_id)

    # Doctor is a "virtual" user not stored in the DB
    if user_id.startswith("doctor_"):
        return User("doctor_admin", "doctor@admin.com", "Dr. Guli", is_doctor=True)

    db = get_db()
    patient = db.execute(
        "SELECT * FROM patients WHERE id = ?", (user_id,)
    ).fetchone()

    if patient:
        return User(patient["id"], patient["email"], patient["name"])
    return None


# ---------- LANGUAGE HELPER ----------


def get_language():
    """Get & remember current language in the session."""
    lang = request.args.get("lang", session.get("language", "uz"))
    session["language"] = lang
    return lang


# ---------- ROUTES ----------


@app.route("/")
def index():
    lang = get_language()
    return render_template("index.html", lang=lang)


@app.route("/about")
def about():
    lang = get_language()
    return render_template("about.html", lang=lang)


@app.route("/appointment", methods=["GET", "POST"])
def appointment():
    lang = get_language()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        date = request.form.get("date", "").strip()
        time = request.form.get("time", "").strip()

        if not all([name, email, phone, date, time]):
            flash("Please fill in all required fields.", "error")
            return redirect(url_for("appointment", lang=lang))

        db = get_db()
        patient = db.execute(
            "SELECT * FROM patients WHERE email = ?", (email,)
        ).fetchone()
        patient_id = patient["id"] if patient else None

        db.execute(
            """INSERT INTO appointments
               (patient_name, patient_email, patient_phone,
                appointment_date, appointment_time, patient_id)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (name, email, phone, date, time, patient_id),
        )
        db.commit()

        flash("Appointment booked successfully!", "success")
        return redirect(url_for("appointment", lang=lang))

    return render_template("appointment.html", lang=lang)


@app.route("/patient/login", methods=["GET", "POST"])
def patient_login():
    lang = get_language()

    if request.method == "POST":
        action = request.form.get("action")

        if action == "register":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip().lower()
            phone = request.form.get("phone", "").strip()
            password = request.form.get("password", "")

            if not all([name, email, password]):
                flash("Name, email and password are required.", "error")
                return redirect(url_for("patient_login", lang=lang))

            db = get_db()
            existing = db.execute(
                "SELECT * FROM patients WHERE email = ?", (email,)
            ).fetchone()

            if existing:
                flash("Email already registered!", "error")
                return redirect(url_for("patient_login", lang=lang))

            password_hash = generate_password_hash(password)
            db.execute(
                "INSERT INTO patients (name, email, phone, password_hash) "
                "VALUES (?, ?, ?, ?)",
                (name, email, phone, password_hash),
            )
            db.commit()

            flash("Registration successful! Please login.", "success")
            return redirect(url_for("patient_login", lang=lang))

        elif action == "login":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")

            db = get_db()
            patient = db.execute(
                "SELECT * FROM patients WHERE email = ?", (email,)
            ).fetchone()

            if patient and check_password_hash(patient["password_hash"], password):
                user = User(patient["id"], patient["email"], patient["name"])
                login_user(user)
                return redirect(url_for("patient_dashboard", lang=lang))
            else:
                flash("Invalid email or password!", "error")

    return render_template("patient_login.html", lang=lang)


@app.route("/patient/dashboard")
@login_required
def patient_dashboard():
    # If somehow doctor hits this route, send them to doctor dashboard
    if getattr(current_user, "is_doctor", False):
        return redirect(url_for("doctor_dashboard"))

    lang = get_language()

    db = get_db()
    appointments = db.execute(
        """SELECT a.*, sn.notes 
           FROM appointments a 
           LEFT JOIN session_notes sn ON a.id = sn.appointment_id
           WHERE a.patient_id = ? 
           ORDER BY a.appointment_date DESC, a.appointment_time DESC""",
        (current_user.id,),
    ).fetchall()

    return render_template(
        "patient_dashboard.html", appointments=appointments, lang=lang
    )


@app.route("/patient/logout")
@login_required
def patient_logout():
    lang = session.get("language", "en")
    logout_user()
    return redirect(url_for("index", lang=lang))


@app.route("/doctor/login", methods=["GET", "POST"])
def doctor_login():
    lang = get_language()

    if request.method == "POST":
        password = request.form.get("password", "")

        if password == DOCTOR_PASSWORD:
            user = User("doctor_admin", "doctor@admin.com", "Dr. Guli", is_doctor=True)
            login_user(user)
            return redirect(url_for("doctor_dashboard", lang=lang))
        else:
            flash("Invalid password!", "error")

    return render_template("doctor_login.html", lang=lang)


@app.route('/doctor/dashboard')
@login_required
def doctor_dashboard():
    if not current_user.is_doctor:
        return redirect(url_for('patient_dashboard'))

    lang = request.args.get('lang', session.get('language', 'en'))
    session['language'] = lang

    db = get_db()
    # show only non-completed appointments
    appointments = db.execute('''
        SELECT a.*, p.name as patient_registered_name, sn.notes, sn.id as note_id
        FROM appointments a
        LEFT JOIN patients p ON a.patient_id = p.id
        LEFT JOIN session_notes sn ON a.id = sn.appointment_id
        WHERE a.status != 'completed'
        ORDER BY a.appointment_date DESC, a.appointment_time DESC
    ''').fetchall()

    patients = db.execute(
        'SELECT * FROM patients ORDER BY created_at DESC'
    ).fetchall()
    db.close()

    return render_template(
        'doctor_dashboard.html',
        appointments=appointments,
        patients=patients,
        lang=lang
    )

@app.route('/doctor/media', methods=['GET', 'POST'])
@login_required
def manage_media():
    """Admin page to add / edit media items (magazines, podcasts, radio, video)."""
    if not current_user.is_doctor:
        return redirect(url_for('index'))

    lang = request.args.get('lang', session.get('language', 'en'))
    session['language'] = lang

    db = get_db()

    # If POST -> create or update item
    if request.method == 'POST':
        media_id = request.form.get('id')  # empty for new item
        media_type = request.form.get('type', 'magazine').strip().lower()
        title_en = request.form.get('title_en', '').strip()
        title_uz = request.form.get('title_uz', '').strip()
        title_ru = request.form.get('title_ru', '').strip()
        description_en = request.form.get('description_en', '').strip()
        description_uz = request.form.get('description_uz', '').strip()
        description_ru = request.form.get('description_ru', '').strip()
        link = request.form.get('link', '').strip()

        if not title_en:
            flash('English title is required.', 'error')
        else:
            if media_id:  # update existing
                db.execute(
                    '''UPDATE magazines
                       SET title_en = ?, title_uz = ?, title_ru = ?,
                           description_en = ?, description_uz = ?, description_ru = ?,
                           link = ?, type = ?
                       WHERE id = ?''',
                    (title_en, title_uz, title_ru,
                     description_en, description_uz, description_ru,
                     link, media_type, media_id)
                )
                flash('Media item updated successfully.', 'success')
            else:  # create new
                db.execute(
                    '''INSERT INTO magazines
                       (title_en, title_uz, title_ru,
                        description_en, description_uz, description_ru,
                        link, type)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                    (title_en, title_uz, title_ru,
                     description_en, description_uz, description_ru,
                     link, media_type)
                )
                flash('Media item added successfully.', 'success')

            db.commit()

        return redirect(url_for('manage_media', lang=lang))

    # GET: fetch list and optional item to edit
    edit_id = request.args.get('media_id')
    edit_item = None
    if edit_id:
        edit_item = db.execute(
            'SELECT * FROM magazines WHERE id = ?',
            (edit_id,)
        ).fetchone()

    items = db.execute(
        'SELECT * FROM magazines ORDER BY created_at DESC'
    ).fetchall()
    db.close()

    return render_template(
        'doctor_media.html',
        items=items,
        edit_item=edit_item,
        lang=lang
    )


@app.route('/doctor/media/<int:media_id>/delete', methods=['POST'])
@login_required
def delete_media(media_id):
    """Delete a media item (doctor only)."""
    if not current_user.is_doctor:
        return redirect(url_for('index'))

    lang = session.get('language', 'en')
    db = get_db()
    db.execute('DELETE FROM magazines WHERE id = ?', (media_id,))
    db.commit()
    db.close()

    flash('Media item deleted.', 'success')
    return redirect(url_for('manage_media', lang=lang))


@app.route("/doctor/add-note/<int:appointment_id>", methods=["POST"])
@login_required
def add_note(appointment_id):
    if not getattr(current_user, "is_doctor", False):
        return redirect(url_for("index"))

    lang = session.get("language", "en")
    notes = request.form.get("notes", "").strip()

    if not notes:
        flash("Notes cannot be empty.", "error")
        return redirect(url_for("doctor_dashboard", lang=lang))

    db = get_db()
    appointment = db.execute(
        "SELECT * FROM appointments WHERE id = ?", (appointment_id,)
    ).fetchone()

    if appointment and appointment["patient_id"]:
        existing_note = db.execute(
            "SELECT * FROM session_notes WHERE appointment_id = ?",
            (appointment_id,),
        ).fetchone()

        if existing_note:
            db.execute(
                "UPDATE session_notes SET notes = ? WHERE appointment_id = ?",
                (notes, appointment_id),
            )
        else:
            db.execute(
                "INSERT INTO session_notes (appointment_id, patient_id, notes) "
                "VALUES (?, ?, ?)",
                (appointment_id, appointment["patient_id"], notes),
            )
        db.commit()
        flash("Session notes saved successfully!", "success")
    else:
        flash("Cannot add notes for unregistered patients!", "error")

    return redirect(url_for("doctor_dashboard", lang=lang))


@app.route("/doctor/logout")
@login_required
def doctor_logout():
    lang = session.get("language", "en")
    logout_user()
    return redirect(url_for("index", lang=lang))


@app.route("/media")
def media():
    lang = get_language()

    # Get search query and type filter from URL
    q = request.args.get("q", "").strip()
    filter_type = request.args.get("type", "").strip().lower()

    db = get_db()

    # Base query
    sql = "SELECT * FROM magazines WHERE 1=1"
    params = []

    # Optional type filter
    if filter_type in ["podcast", "magazine", "radio", "video"]:
        sql += " AND type = ?"
        params.append(filter_type)

    # Optional text search across all languages
    if q:
        like = f"%{q}%"
        sql += """
            AND (
                title_en LIKE ? OR title_uz LIKE ? OR title_ru LIKE ?
                OR description_en LIKE ? OR description_uz LIKE ? OR description_ru LIKE ?
            )
        """
        params.extend([like] * 6)

    sql += " ORDER BY created_at DESC"

    content = db.execute(sql, params).fetchall()

    return render_template(
        "media.html",
        content=content,
        lang=lang,
        q=q,
        filter_type=filter_type,
    )

@app.route('/doctor/appointment/<int:appointment_id>/status', methods=['POST'])
@login_required
def update_appointment_status(appointment_id):
    if not current_user.is_doctor:
        return redirect(url_for('index'))

    lang = request.args.get('lang', session.get('language', 'en'))
    session['language'] = lang

    new_status = request.form.get('status', 'scheduled')

    db = get_db()
    db.execute(
        'UPDATE appointments SET status = ? WHERE id = ?',
        (new_status, appointment_id)
    )
    db.commit()
    db.close()

    flash('Appointment status updated.', 'success')
    return redirect(url_for('doctor_dashboard', lang=lang))



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
