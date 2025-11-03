# Dr. Guli Bekmurodovna - Psychotherapy Practice Website

## Overview
A professional, multilingual psychotherapy practice website for Dr. Guli Bekmurodovna, featuring appointment booking, patient management, and a password-protected doctor dashboard.

## Project Information
- **Technology Stack**: Flask (Python), SQLite, Bootstrap 5, JavaScript
- **Languages Supported**: English, Uzbek, Russian
- **Theme**: Light/Dark mode with psychology-themed colors (calming teals, sage greens, warm neutrals)

## Key Features
1. **Homepage**: Professional introduction with Dr. Guli's photo and specializations
2. **Appointment Booking**: Walk-in booking without registration required
3. **Patient Portal**: Combined registration/login page for accessing session notes
4. **Doctor Dashboard**: Password-protected management interface
5. **About Page**: Complete biography, contact information, and social media links
6. **Media Page**: Showcase of magazines and podcasts
7. **Multi-language Support**: Full translations across all pages
8. **Theme Toggle**: Light/dark mode with persistent preferences

## Contact Information
- **Phone**: +393314086000
- **Email**: guliturayeva@psychologist.com
- **Instagram**: dr.guli_bekmurodova

## Doctor Dashboard Access
- **Password**: DrGuli2024
- Access via: Footer "Doctor Login" link or `/doctor/login`

## Database Schema
- **patients**: Registered patient accounts
- **appointments**: All scheduled appointments (both registered and walk-in)
- **session_notes**: Doctor's notes for registered patients
- **magazines**: Published content and media appearances

## Color Scheme
Light Mode:
- Primary: #4A90A4 (Calming Teal)
- Secondary: #87BBA2 (Sage Green)
- Accent: #C7956D (Warm Neutral)

Dark Mode:
- Automatically adjusts for comfortable night viewing

## Recent Changes
- Initial website creation (Nov 3, 2024)
- Complete multilingual support implemented
- Doctor dashboard with patient management
- Session notes system for registered patients

## Architecture
```
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── templates/               # HTML templates
│   ├── base.html           # Base template with navigation
│   ├── index.html          # Homepage
│   ├── about.html          # About page
│   ├── appointment.html    # Booking page
│   ├── patient_login.html  # Patient registration/login
│   ├── patient_dashboard.html
│   ├── doctor_login.html
│   ├── doctor_dashboard.html
│   └── media.html
├── static/
│   ├── css/
│   │   └── style.css       # Main stylesheet with theme support
│   ├── js/
│   │   ├── translations.js # Translation dictionary
│   │   └── main.js         # Theme toggle & language switching
│   └── images/
│       └── dr-guli.png     # Doctor's professional photo
└── therapy.db              # SQLite database (auto-created)
```

## User Workflows

### For Patients
1. **Book Appointment** (No Registration):
   - Navigate to "Appointment" page
   - Fill in name, email, phone, date, and time
   - Submit booking

2. **Register & View Session Notes**:
   - Go to "Patient Login" page
   - Fill registration form on right side
   - After registration, login to view appointments and session notes

### For Doctor
1. **Login**:
   - Click "Doctor Login" in footer or navigate to `/doctor/login`
   - Enter password: DrGuli2024

2. **Manage Appointments**:
   - View all scheduled appointments
   - Add/edit session notes for registered patients

3. **View Registered Patients**:
   - Switch to "Registered Patients" tab
   - View complete patient list with contact information

## Notes
- Database is auto-created on first run with sample magazine/podcast content
- Session notes can only be added for registered patients
- Theme preference persists in browser localStorage
- Language selection persists in session
