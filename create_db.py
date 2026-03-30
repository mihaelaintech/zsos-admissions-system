import sqlite3
from datetime import datetime

conn = sqlite3.connect("admissions.db")
cursor = conn.cursor()

# Drop old tables
cursor.execute("DROP TABLE IF EXISTS documents")
cursor.execute("DROP TABLE IF EXISTS applicants")
cursor.execute("DROP TABLE IF EXISTS users")

# Create users table
cursor.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL,
    full_name TEXT,
    email TEXT
)
""")

# Create applicants table
cursor.execute("""
CREATE TABLE applicants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    created_by_staff_id INTEGER,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT,
    campus_city TEXT,
    study_level TEXT,
    intake TEXT,
    application_type TEXT,
    study_mode TEXT,
    course_interest TEXT,
    university_interest TEXT,
    course_duration TEXT,
    status TEXT NOT NULL,
    notes TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (created_by_staff_id) REFERENCES users(id)
)
""")

# Create documents table
cursor.execute("""
CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    applicant_id INTEGER NOT NULL,
    cv_uploaded INTEGER NOT NULL DEFAULT 0,
    passport_uploaded INTEGER NOT NULL DEFAULT 0,
    transcript_uploaded INTEGER NOT NULL DEFAULT 0,
    personal_statement_uploaded INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (applicant_id) REFERENCES applicants(id)
)
""")

# Seed users
users = [
    ("manager1", "manager123", "manager", "Operations Manager", "manager1@zsosdemo.com"),
    ("adviser1", "adviser123", "student_adviser", "Anna Student Adviser", "adviser1@zsosdemo.com"),
    ("adviser2", "adviser123", "student_adviser", "David Student Adviser", "adviser2@zsosdemo.com"),
    ("mihaelapetre1", "student123", "student", "Mihaela Petre", "mihaela@student.com"),
    ("drake1", "drake123", "student", "Drake Adams", "drake1@gmail.com"),
    ("lewis1", "lewis123", "student", "Lewis Anderson", "lewis1@gmail.com"),
    ("eliot1", "eliot123", "student", "Eliot William Bailey", "eliot1@gmail.com"),
    ("tudor1", "tudor123", "student", "Tudor Boswell", "tudor1@gmail.com"),
    ("georgia1", "georgia123", "student", "Georgia Elaine Campbell", "georgia1@gmail.com"),
    ("kim1", "kim123", "student", "Kim Anais Byron", "kim1@gmail.com"),
    ("judy1", "judy123", "student", "Judy Cohen", "judy1@gmail.com"),
    ("olivia1", "olivia123", "student", "Olivia Louisa Adams", "olivia1@gmail.com")
]

cursor.executemany("""
INSERT INTO users (username, password, role, full_name, email)
VALUES (?, ?, ?, ?, ?)
""", users)

# Get user IDs
cursor.execute("SELECT id FROM users WHERE username = 'manager1'")
manager_id = cursor.fetchone()[0]

cursor.execute("SELECT id FROM users WHERE username = 'adviser1'")
adviser1_id = cursor.fetchone()[0]

cursor.execute("SELECT id FROM users WHERE username = 'adviser2'")
adviser2_id = cursor.fetchone()[0]

student_ids = {}
for username in ["mihaelapetre1", "drake1", "lewis1", "eliot1", "tudor1", "georgia1", "kim1", "judy1", "olivia1"]:
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    student_ids[username] = cursor.fetchone()[0]

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

applicants = [
    (
        student_ids["mihaelapetre1"], adviser1_id, "Mihaela Petre", "mihaela@student.com", "07991111111",
        "Manchester", "Postgraduate", "September 2026", "Direct Application", "Full-time",
        "International Business Management with Project Management - MSc",
        "Elizabeth School of London", "1 Year", "Documents Received",
        "Interested in September intake.", now, now
    ),
    (
        student_ids["drake1"], adviser1_id, "Drake Adams", "drake1@gmail.com", "0799000000",
        "London", "Undergraduate", "September 2026", "Direct Application", "Full-time",
        "BA (Hons) Business and Management", "London Metropolitan University", "3 Years",
        "New Lead", "Initial enquiry received.", now, now
    ),
    (
        student_ids["lewis1"], adviser1_id, "Lewis Anderson", "lewis1@gmail.com", "0799000100",
        "London", "Undergraduate", "September 2026", "Partner Referral", "Full-time",
        "Accounting and Finance - BA (Hons)", "Elizabeth School of London", "3 Years",
        "Documents Received", "Awaiting transcript.", now, now
    ),
    (
        student_ids["eliot1"], adviser1_id, "Eliot William Bailey", "eliot1@gmail.com", "0799000200",
        "London", "Undergraduate", "September 2026", "Direct Application", "Full-time",
        "Computer Science - BSc (Hons)", "London Metropolitan University", "3 Years",
        "Interview Scheduled", "Interview booked for next week.", now, now
    ),
    (
        student_ids["tudor1"], adviser2_id, "Tudor Boswell", "tudor1@gmail.com", "0799000300",
        "London", "Undergraduate", "September 2026", "Internal Enquiry Conversion", "Full-time",
        "Mathematical Sciences - BSc (Hons)", "London Metropolitan University", "3 Years",
        "Documents Verified", "All academic documents checked.", now, now
    ),
    (
        student_ids["georgia1"], adviser2_id, "Georgia Elaine Campbell", "georgia1@gmail.com", "0799000400",
        "London", "Undergraduate", "September 2026", "Partner Referral", "Full-time",
        "BSc (Hons) Psychology with Counselling and Mental Health",
        "Elizabeth School of London", "3 Years",
        "Application Submitted", "Submitted to partner portal.", now, now
    ),
    (
        student_ids["kim1"], adviser2_id, "Kim Anais Byron", "kim1@gmail.com", "0799000500",
        "Manchester", "Undergraduate", "September 2026", "Direct Application", "Full-time",
        "BSc (Hons) Health and Social Care", "Arden University", "3 Years",
        "Offer Received", "Conditional offer received.", now, now
    ),
    (
        student_ids["judy1"], adviser2_id, "Judy Cohen", "judy1@gmail.com", "0799000600",
        "Manchester", "Undergraduate", "September 2026", "Direct Application", "Full-time",
        "BA (Hons) Criminology with Law", "Elizabeth School of London", "3 Years",
        "New Lead", "Needs guidance on intake.", now, now
    ),
    (
        student_ids["olivia1"], adviser1_id, "Olivia Louisa Adams", "olivia1@gmail.com", "0799000700",
        "Manchester", "Undergraduate", "September 2026", "Direct Application", "Full-time",
        "BSc (Hons) Computing with Foundation Year", "Arden University", "4 Years",
        "Documents Received", "Passport uploaded, transcript pending.", now, now
    )
]

cursor.executemany("""
INSERT INTO applicants (
    user_id,
    created_by_staff_id,
    full_name,
    email,
    phone,
    campus_city,
    study_level,
    intake,
    application_type,
    study_mode,
    course_interest,
    university_interest,
    course_duration,
    status,
    notes,
    created_at,
    updated_at
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", applicants)

# Create documents for each applicant
cursor.execute("SELECT id, email FROM applicants")
all_applicants = cursor.fetchall()

for applicant_id, email in all_applicants:
    if email == "drake1@gmail.com":
        docs = (applicant_id, 0, 0, 0, 0)
    elif email == "lewis1@gmail.com":
        docs = (applicant_id, 1, 1, 0, 0)
    elif email == "eliot1@gmail.com":
        docs = (applicant_id, 1, 1, 1, 1)
    elif email == "tudor1@gmail.com":
        docs = (applicant_id, 1, 1, 1, 1)
    elif email == "georgia1@gmail.com":
        docs = (applicant_id, 1, 1, 1, 1)
    elif email == "kim1@gmail.com":
        docs = (applicant_id, 1, 1, 1, 1)
    elif email == "judy1@gmail.com":
        docs = (applicant_id, 0, 0, 0, 0)
    elif email == "olivia1@gmail.com":
        docs = (applicant_id, 1, 1, 0, 0)
    else:
        docs = (applicant_id, 1, 0, 0, 0)

    cursor.execute("""
    INSERT INTO documents (
        applicant_id,
        cv_uploaded,
        passport_uploaded,
        transcript_uploaded,
        personal_statement_uploaded
    )
    VALUES (?, ?, ?, ?, ?)
    """, docs)

conn.commit()
conn.close()

print("Database created successfully with demo data.")