
from flask import Flask, request, jsonify, send_from_directory
import sqlite3
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "jobs.db")


# Database connection
def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


# Create database tables
def initialize_database():
    connection = get_db()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            title TEXT NOT NULL,
            location TEXT NOT NULL,
            salary TEXT NOT NULL,
            job_type TEXT NOT NULL
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            applicant_name TEXT NOT NULL,
            email TEXT NOT NULL,
            FOREIGN KEY (job_id) REFERENCES jobs(id)
        )
    """)

    # Add sample jobs only when the database is empty
    count = connection.execute(
        "SELECT COUNT(*) FROM jobs"
    ).fetchone()[0]

    if count == 0:
        sample_jobs = [
            ("Google", "Software Developer", "Bengaluru", "12-18 LPA", "Full Time"),
            ("Amazon", "Frontend Developer", "Hyderabad", "8-14 LPA", "Full Time"),
            ("Microsoft", "Data Analyst", "Noida", "10-16 LPA", "Full Time"),
            ("Infosys", "Python Developer", "Pune", "5-8 LPA", "Full Time"),
            ("TCS", "AI Intern", "Remote", "3-5 LPA", "Internship")
        ]

        connection.executemany("""
            INSERT INTO jobs (company, title, location, salary, job_type)
            VALUES (?, ?, ?, ?, ?)
        """, sample_jobs)

    connection.commit()
    connection.close()
    print("Job Portal database initialized successfully!")


# Homepage
@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")


# Serve CSS and JavaScript
@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(BASE_DIR, filename)


# Get all jobs
@app.route("/api/jobs", methods=["GET"])
def get_jobs():
    connection = get_db()
    jobs = connection.execute(
        "SELECT * FROM jobs ORDER BY id DESC"
    ).fetchall()
    connection.close()

    return jsonify([dict(job) for job in jobs])


# Post a new job
@app.route("/api/jobs", methods=["POST"])
def create_job():
    data = request.get_json(silent=True) or {}

    company = str(data.get("company", "")).strip()
    title = str(data.get("title", "")).strip()
    location = str(data.get("location", "")).strip()
    salary = str(data.get("salary", "")).strip()
    job_type = str(data.get("job_type", "")).strip()

    if not all([company, title, location, salary, job_type]):
        return jsonify({"error": "Please fill in all job details."}), 400

    if job_type not in ["Full Time", "Part Time", "Internship"]:
        return jsonify({"error": "Invalid job type."}), 400

    connection = get_db()

    cursor = connection.execute("""
        INSERT INTO jobs (company, title, location, salary, job_type)
        VALUES (?, ?, ?, ?, ?)
    """, (company, title, location, salary, job_type))

    connection.commit()
    job_id = cursor.lastrowid
    connection.close()

    return jsonify({
        "message": "Job posted successfully!",
        "id": job_id
    }), 201


# Apply for a job
@app.route("/api/applications", methods=["POST"])
def create_application():
    data = request.get_json(silent=True) or {}

    job_id = data.get("job_id")
    applicant_name = str(data.get("applicant_name", "")).strip()
    email = str(data.get("email", "")).strip()

    if not job_id or not applicant_name or not email:
        return jsonify({"error": "Please provide all application details."}), 400

    if "@" not in email or "." not in email:
        return jsonify({"error": "Please enter a valid email address."}), 400

    try:
        job_id = int(job_id)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid job ID."}), 400

    connection = get_db()

    job = connection.execute(
        "SELECT id FROM jobs WHERE id = ?", (job_id,)
    ).fetchone()

    if job is None:
        connection.close()
        return jsonify({"error": "Job not found."}), 404

    connection.execute("""
        INSERT INTO applications (job_id, applicant_name, email)
        VALUES (?, ?, ?)
    """, (job_id, applicant_name, email))

    connection.commit()
    connection.close()

    return jsonify({"message": "Application submitted successfully!"}), 201


# View all applications
@app.route("/api/applications", methods=["GET"])
def get_applications():
    connection = get_db()

    applications = connection.execute("""
        SELECT
            applications.id,
            applications.applicant_name,
            applications.email,
            jobs.title AS job_title,
            jobs.company
        FROM applications
        JOIN jobs ON applications.job_id = jobs.id
        ORDER BY applications.id DESC
    """).fetchall()

    connection.close()

    return jsonify([dict(application) for application in applications])


# Run application
if __name__ == "__main__":
    initialize_database()
    print("JobConnect Portal starting...")
    app.run(host="127.0.0.1", port=5000, debug=False)
