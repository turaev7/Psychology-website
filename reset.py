from app import app, get_db

# Run this with:
#   (venv) python reset.py
#
# It will:
#   - delete all session notes
#   - delete all appointments
#   - delete all patients
#   - keep all media in "magazines"

with app.app_context():
    db = get_db()

    # 1. Delete notes (they depend on appointments & patients)
    db.execute("DELETE FROM session_notes")

    # 2. Delete all appointments
    db.execute("DELETE FROM appointments")

    # 3. Delete all patients (doctor is virtual, not in DB)
    db.execute("DELETE FROM patients")

    db.commit()
    print("✅ Cleared: patients, appointments, and session notes. Media is untouched.")
