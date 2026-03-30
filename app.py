from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime
from functools import wraps
import re

app = Flask(__name__)
app.secret_key = "zsos_secret_key_demo"

UNIVERSITIES = [
    "London Metropolitan University",
    "Arden University",
    "Elizabeth School of London"
]

COURSES = [
    "Accounting and Finance - BA (Hons)",
    "Computer Science - BSc (Hons)",
    "Mathematical Sciences - BSc (Hons)",
    "Nursing (Adult) - BSc (Hons)",
    "Pharmaceutical Science - BSc (Hons)",
    "Civil Engineering with Project Management - MSc",
    "Computer Networking and Cyber Security - MSc",
    "Criminology - MSc",
    "International Business Management with Project Management - MSc",
    "BSc (Hons) Psychology with Counselling and Mental Health",
    "BA (Hons) Criminology with Law",
    "MSc Strategic Human Resource Management",
    "MSc Accounting and Finance",
    "BA (Hons) Business Management and Marketing with Foundation Year",
    "BA (Hons) Business and Management with Foundation Year",
    "BA (Hons) Business and Management",
    "BSc (Hons) Health and Social Care Management with Foundation Year",
    "BSc (Hons) Health and Social Care",
    "BSc (Hons) Computing with Foundation Year"
]

CAMPUS_CITIES = ["London", "Manchester", "Birmingham", "Leeds", "Online"]
STUDY_LEVELS = ["Undergraduate", "Postgraduate", "Foundation Year"]
INTAKES = ["September 2026", "January 2027", "May 2027"]
APPLICATION_TYPES = ["Direct Application", "Partner Referral", "Internal Enquiry Conversion"]
STUDY_MODES = ["Full-time", "Part-time", "Online"]
COURSE_DURATIONS = ["1 Year", "2 Years", "3 Years", "4 Years"]
STATUSES = [
    "New Lead",
    "Documents Received",
    "Documents Verified",
    "Interview Scheduled",
    "Application Submitted",
    "Offer Received"
]

STAFF_ROLES = ["student_adviser", "manager"]


def get_db():
    conn = sqlite3.connect("admissions.db")
    conn.row_factory = sqlite3.Row
    return conn


def current_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def generate_student_credentials(email: str):
    local_part = email.split("@")[0].strip().lower()
    username = local_part

    password_base = re.sub(r"\d+$", "", local_part)
    if not password_base:
        password_base = local_part

    password = password_base + "123"
    return username, password


def ensure_unique_username(cursor, username: str):
    candidate = username
    counter = 1

    cursor.execute("SELECT id FROM users WHERE username = ?", (candidate,))
    existing = cursor.fetchone()

    while existing:
        candidate = f"{username}{counter}"
        cursor.execute("SELECT id FROM users WHERE username = ?", (candidate,))
        existing = cursor.fetchone()
        counter += 1

    return candidate


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return decorated_function


def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "role" not in session:
                return redirect(url_for("home"))
            if session["role"] != required_role:
                return "<h1>Access denied</h1>", 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def staff_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "role" not in session:
            return redirect(url_for("home"))
        if session["role"] not in STAFF_ROLES:
            return "<h1>Access denied</h1>", 403
        return f(*args, **kwargs)
    return decorated_function


def can_modify_applicant(applicant, current_user_id, current_user_role):
    if current_user_role == "manager":
        return True
    if current_user_role == "student_adviser":
        return applicant["created_by_staff_id"] == current_user_id
    return False


def get_form_options():
    return {
        "universities": UNIVERSITIES,
        "courses": COURSES,
        "campus_cities": CAMPUS_CITIES,
        "study_levels": STUDY_LEVELS,
        "intakes": INTAKES,
        "application_types": APPLICATION_TYPES,
        "study_modes": STUDY_MODES,
        "course_durations": COURSE_DURATIONS,
        "statuses": STATUSES
    }


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None

    if request.method == "POST":
        full_name = request.form["full_name"].strip()
        email = request.form["email"].strip().lower()
        campus_city = request.form["campus_city"].strip()
        study_level = request.form["study_level"].strip()
        intake = request.form["intake"].strip()
        application_type = request.form["application_type"].strip()
        study_mode = request.form["study_mode"].strip()
        university_interest = request.form["university_interest"].strip()
        course_interest = request.form["course_interest"].strip()
        course_duration = request.form["course_duration"].strip()
        notes = request.form["notes"].strip()

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM applicants WHERE email = ?", (email,))
        existing_email = cursor.fetchone()
        if existing_email:
            conn.close()
            error = "An applicant with this email already exists."
            return render_template("register.html", error=error, **get_form_options())

        base_username, password = generate_student_credentials(email)
        username = ensure_unique_username(cursor, base_username)

        created_at = current_timestamp()

        cursor.execute("""
            INSERT INTO users (username, password, role, full_name, email)
            VALUES (?, ?, ?, ?, ?)
        """, (username, password, "student", full_name, email))
        user_id = cursor.lastrowid

        cursor.execute("""
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
        """, (
            user_id,
            None,
            full_name,
            email,
            "",
            campus_city,
            study_level,
            intake,
            application_type,
            study_mode,
            course_interest,
            university_interest,
            course_duration,
            "New Lead",
            notes,
            created_at,
            created_at
        ))

        applicant_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO documents (
                applicant_id,
                cv_uploaded,
                passport_uploaded,
                transcript_uploaded,
                personal_statement_uploaded
            )
            VALUES (?, ?, ?, ?, ?)
        """, (applicant_id, 0, 0, 0, 0))

        conn.commit()
        conn.close()

        return render_template(
            "register_success.html",
            full_name=full_name,
            email=email,
            generated_username=username
        )

    return render_template("register.html", error=error, **get_form_options())


@app.route("/student_login", methods=["GET", "POST"])
def student_login():
    error = None

    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM users
            WHERE username = ? AND password = ? AND role = 'student'
        """, (username, password))
        user = cursor.fetchone()

        conn.close()

        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            return redirect(url_for("student_home"))
        else:
            error = "Invalid student username or password."

    return render_template("student_login.html", error=error)


@app.route("/staff_login", methods=["GET", "POST"])
def staff_login():
    error = None

    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM users
            WHERE username = ? AND password = ?
              AND role IN ('student_adviser', 'manager')
        """, (username, password))
        user = cursor.fetchone()

        conn.close()

        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid staff username or password."

    return render_template("staff_login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/help")
@login_required
def help_page():
    return render_template("help.html")


@app.route("/profile")
@login_required
def profile():
    conn = get_db()
    cursor = conn.cursor()

    user_row = None

    if session.get("role") == "student":
        cursor.execute("""
            SELECT full_name, email
            FROM applicants
            WHERE user_id = ?
        """, (session["user_id"],))
        user_row = cursor.fetchone()

    elif session.get("role") in STAFF_ROLES:
        cursor.execute("""
            SELECT full_name, email
            FROM users
            WHERE id = ?
        """, (session["user_id"],))
        user_row = cursor.fetchone()

    conn.close()

    return render_template("profile.html", user_row=user_row)


@app.route("/dashboard")
@login_required
@staff_required
def dashboard():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM applicants")
    total_applicants = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM documents
        WHERE cv_uploaded = 0
           OR passport_uploaded = 0
           OR transcript_uploaded = 0
           OR personal_statement_uploaded = 0
    """)
    pending_documents = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM applicants
        WHERE status = 'Interview Scheduled'
    """)
    interview_scheduled = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM applicants
        WHERE status = 'Offer Received'
    """)
    offers_received = cursor.fetchone()[0]

    cursor.execute("""
        SELECT status, COUNT(*) AS total
        FROM applicants
        GROUP BY status
        ORDER BY total DESC, status ASC
    """)
    status_counts = cursor.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        total_applicants=total_applicants,
        pending_documents=pending_documents,
        interview_scheduled=interview_scheduled,
        offers_received=offers_received,
        status_counts=status_counts
    )
@app.route("/student/home")
@login_required
@role_required("student")
def student_home():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM applicants
        WHERE user_id = ?
    """, (session["user_id"],))
    applicant = cursor.fetchone()

    documents = None
    if applicant:
        cursor.execute("""
            SELECT *
            FROM documents
            WHERE applicant_id = ?
        """, (applicant["id"],))
        documents = cursor.fetchone()

    conn.close()

    return render_template(
        "student_home.html",
        applicant=applicant,
        documents=documents,
        **get_form_options()
    )


@app.route("/student/update_application", methods=["POST"])
@login_required
@role_required("student")
def student_update_application():
    phone = request.form["phone"].strip()
    campus_city = request.form["campus_city"].strip()
    study_level = request.form["study_level"].strip()
    intake = request.form["intake"].strip()
    application_type = request.form["application_type"].strip()
    study_mode = request.form["study_mode"].strip()
    course_interest = request.form["course_interest"].strip()
    university_interest = request.form["university_interest"].strip()
    course_duration = request.form["course_duration"].strip()
    notes = request.form["notes"].strip()

    cv_uploaded = 1 if request.form.get("cv_uploaded") else 0
    passport_uploaded = 1 if request.form.get("passport_uploaded") else 0
    transcript_uploaded = 1 if request.form.get("transcript_uploaded") else 0
    personal_statement_uploaded = 1 if request.form.get("personal_statement_uploaded") else 0

    updated_at = current_timestamp()

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM applicants
        WHERE user_id = ?
    """, (session["user_id"],))
    applicant = cursor.fetchone()

    if applicant:
        cursor.execute("""
            UPDATE applicants
            SET phone = ?,
                campus_city = ?,
                study_level = ?,
                intake = ?,
                application_type = ?,
                study_mode = ?,
                course_interest = ?,
                university_interest = ?,
                course_duration = ?,
                notes = ?,
                updated_at = ?
            WHERE id = ?
        """, (
            phone,
            campus_city,
            study_level,
            intake,
            application_type,
            study_mode,
            course_interest,
            university_interest,
            course_duration,
            notes,
            updated_at,
            applicant["id"]
        ))

        cursor.execute("""
            UPDATE documents
            SET cv_uploaded = ?,
                passport_uploaded = ?,
                transcript_uploaded = ?,
                personal_statement_uploaded = ?
            WHERE applicant_id = ?
        """, (
            cv_uploaded,
            passport_uploaded,
            transcript_uploaded,
            personal_statement_uploaded,
            applicant["id"]
        ))

    conn.commit()
    conn.close()

    return redirect(url_for("student_home"))


@app.route("/applicants")
@login_required
@staff_required
def view_applicants():
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()

    conn = get_db()
    cursor = conn.cursor()

    query = """
        SELECT applicants.*,
               users.full_name AS created_by_name
        FROM applicants
        LEFT JOIN users ON applicants.created_by_staff_id = users.id
        WHERE 1=1
    """
    params = []

    if search:
        query += " AND (applicants.full_name LIKE ? OR applicants.email LIKE ?)"
        like_term = f"%{search}%"
        params.extend([like_term, like_term])

    if status:
        query += " AND applicants.status = ?"
        params.append(status)

    query += " ORDER BY applicants.created_at DESC"

    cursor.execute(query, params)
    applicants = cursor.fetchall()

    conn.close()

    return render_template(
        "applicants.html",
        applicants=applicants,
        search=search,
        selected_status=status,
        statuses=STATUSES
    )


@app.route("/applicant/<int:applicant_id>")
@login_required
@staff_required
def applicant_detail(applicant_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT applicants.*,
               users.full_name AS created_by_name
        FROM applicants
        LEFT JOIN users ON applicants.created_by_staff_id = users.id
        WHERE applicants.id = ?
    """, (applicant_id,))
    applicant = cursor.fetchone()

    cursor.execute("""
        SELECT *
        FROM documents
        WHERE applicant_id = ?
    """, (applicant_id,))
    documents = cursor.fetchone()

    conn.close()

    if applicant is None:
        return "<h1>Applicant not found</h1>", 404

    return render_template(
        "applicant_detail.html",
        applicant=applicant,
        documents=documents
    )


@app.route("/edit_applicant/<int:applicant_id>", methods=["GET", "POST"])
@login_required
@staff_required
def edit_applicant(applicant_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM applicants WHERE id = ?", (applicant_id,))
    applicant = cursor.fetchone()

    cursor.execute("SELECT * FROM documents WHERE applicant_id = ?", (applicant_id,))
    documents = cursor.fetchone()

    if applicant is None:
        conn.close()
        return "<h1>Applicant not found</h1>", 404

    if not can_modify_applicant(applicant, session["user_id"], session["role"]):
        conn.close()
        return "<h1>Access denied: you can only edit applicants you created.</h1>", 403

    if request.method == "POST":
        full_name = request.form["full_name"].strip()
        email = request.form["email"].strip().lower()
        phone = request.form["phone"].strip()
        campus_city = request.form["campus_city"].strip()
        study_level = request.form["study_level"].strip()
        intake = request.form["intake"].strip()
        application_type = request.form["application_type"].strip()
        study_mode = request.form["study_mode"].strip()
        course_interest = request.form["course_interest"].strip()
        university_interest = request.form["university_interest"].strip()
        course_duration = request.form["course_duration"].strip()
        status = request.form["status"].strip()
        notes = request.form["notes"].strip()

        cv_uploaded = 1 if request.form.get("cv_uploaded") else 0
        passport_uploaded = 1 if request.form.get("passport_uploaded") else 0
        transcript_uploaded = 1 if request.form.get("transcript_uploaded") else 0
        personal_statement_uploaded = 1 if request.form.get("personal_statement_uploaded") else 0

        updated_at = current_timestamp()

        cursor.execute("SELECT id FROM applicants WHERE email = ? AND id != ?", (email, applicant_id))
        existing_email = cursor.fetchone()
        if existing_email:
            conn.close()
            return "<h1>Email already exists for another applicant.</h1>", 400

        if applicant["user_id"]:
            cursor.execute("""
                UPDATE users
                SET full_name = ?, email = ?
                WHERE id = ?
            """, (full_name, email, applicant["user_id"]))

        cursor.execute("""
            UPDATE applicants
            SET full_name = ?,
                email = ?,
                phone = ?,
                campus_city = ?,
                study_level = ?,
                intake = ?,
                application_type = ?,
                study_mode = ?,
                course_interest = ?,
                university_interest = ?,
                course_duration = ?,
                status = ?,
                notes = ?,
                updated_at = ?
            WHERE id = ?
        """, (
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
            updated_at,
            applicant_id
        ))

        cursor.execute("""
            UPDATE documents
            SET cv_uploaded = ?,
                passport_uploaded = ?,
                transcript_uploaded = ?,
                personal_statement_uploaded = ?
            WHERE applicant_id = ?
        """, (
            cv_uploaded,
            passport_uploaded,
            transcript_uploaded,
            personal_statement_uploaded,
            applicant_id
        ))

        conn.commit()
        conn.close()

        return redirect(url_for("applicant_detail", applicant_id=applicant_id))

    conn.close()
    return render_template(
        "edit_applicant.html",
        applicant=applicant,
        documents=documents,
        **get_form_options()
    )


@app.route("/delete_applicant/<int:applicant_id>", methods=["POST"])
@login_required
@staff_required
def delete_applicant(applicant_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM applicants WHERE id = ?", (applicant_id,))
    applicant = cursor.fetchone()

    if applicant is None:
        conn.close()
        return "<h1>Applicant not found</h1>", 404

    if not can_modify_applicant(applicant, session["user_id"], session["role"]):
        conn.close()
        return "<h1>Access denied: you can only delete applicants you created.</h1>", 403

    user_id = applicant["user_id"]

    cursor.execute("DELETE FROM documents WHERE applicant_id = ?", (applicant_id,))
    cursor.execute("DELETE FROM applicants WHERE id = ?", (applicant_id,))

    if user_id:
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))

    conn.commit()
    conn.close()

    return redirect(url_for("view_applicants"))


@app.route("/add_applicant", methods=["GET", "POST"])
@login_required
@staff_required
def add_applicant():
    error = None

    if request.method == "POST":
        full_name = request.form["full_name"].strip()
        email = request.form["email"].strip().lower()
        phone = request.form["phone"].strip()
        campus_city = request.form["campus_city"].strip()
        study_level = request.form["study_level"].strip()
        intake = request.form["intake"].strip()
        application_type = request.form["application_type"].strip()
        study_mode = request.form["study_mode"].strip()
        course_interest = request.form["course_interest"].strip()
        university_interest = request.form["university_interest"].strip()
        course_duration = request.form["course_duration"].strip()
        status = request.form["status"].strip()
        notes = request.form["notes"].strip()

        cv_uploaded = 1 if request.form.get("cv_uploaded") else 0
        passport_uploaded = 1 if request.form.get("passport_uploaded") else 0
        transcript_uploaded = 1 if request.form.get("transcript_uploaded") else 0
        personal_statement_uploaded = 1 if request.form.get("personal_statement_uploaded") else 0

        created_at = current_timestamp()

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM applicants WHERE email = ?", (email,))
        existing_email = cursor.fetchone()
        if existing_email:
            conn.close()
            error = "An applicant with this email already exists."
            return render_template("add_applicant.html", error=error, **get_form_options())

        base_username, password = generate_student_credentials(email)
        username = ensure_unique_username(cursor, base_username)

        cursor.execute("""
            INSERT INTO users (username, password, role, full_name, email)
            VALUES (?, ?, ?, ?, ?)
        """, (username, password, "student", full_name, email))
        user_id = cursor.lastrowid

        cursor.execute("""
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
        """, (
            user_id,
            session["user_id"],
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
            created_at
        ))

        applicant_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO documents (
                applicant_id,
                cv_uploaded,
                passport_uploaded,
                transcript_uploaded,
                personal_statement_uploaded
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            applicant_id,
            cv_uploaded,
            passport_uploaded,
            transcript_uploaded,
            personal_statement_uploaded
        ))

        conn.commit()
        conn.close()

        return render_template(
            "student_credentials.html",
            full_name=full_name,
            email=email,
            generated_username=username,
            generated_password=password
        )

    return render_template("add_applicant.html", error=error, **get_form_options())


if __name__ == "__main__":
    app.run(debug=True)