
import os
import re
import sqlite3
from flask import Flask, jsonify, render_template, request
from docx import Document
from pypdf import PdfReader

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "resumes.db")

TARGET_SKILLS = [
    "python", "flask", "django", "sql", "mysql", "postgresql",
    "git", "github", "html", "css", "javascript", "react",
    "docker", "rest api", "linux", "aws", "machine learning",
    "pandas", "numpy"
]


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                score INTEGER,
                found_skills TEXT,
                missing_skills TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


init_db()


def extract_text(file):
    filename = file.filename.lower()

    if filename.endswith(".pdf"):
        reader = PdfReader(file)
        return "\n".join(
            page.extract_text() or "" for page in reader.pages
        ).strip()

    if filename.endswith(".docx"):
        doc = Document(file)
        return "\n".join(
            p.text for p in doc.paragraphs if p.text
        ).strip()

    raise ValueError("Please upload a PDF or DOCX resume.")


def find_skills(text):
    text = text.lower()
    found = []

    for skill in TARGET_SKILLS:
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"
        if re.search(pattern, text):
            found.append(skill)

    return found


def display_skills(skills):
    return [skill.title() for skill in skills]


def analyze_resume_text(resume_text, job_description=""):
    resume_skills = find_skills(resume_text)

    # Use the entered job description to determine requirements.
    # If none is entered, use the built-in skill list.
    if job_description.strip():
        required_skills = find_skills(job_description)

        if not required_skills:
            return {
                "error": (
                    "No recognized technical skills were found "
                    "in the job description. Try mentioning skills "
                    "such as Python, SQL, Flask, or Docker."
                )
            }
    else:
        required_skills = TARGET_SKILLS.copy()

    found_skills = [
        skill for skill in required_skills
        if skill in resume_skills
    ]

    missing_skills = [
        skill for skill in required_skills
        if skill not in resume_skills
    ]

    score = round(
        len(found_skills) / len(required_skills) * 100
    ) if required_skills else 0

    recommendations = []

    if missing_skills:
        recommendations.append(
            "Consider learning or gaining experience in: "
            + ", ".join(display_skills(missing_skills))
        )

    if "git" not in resume_skills and "github" not in resume_skills:
        recommendations.append(
            "Consider adding relevant version-control experience."
        )

    if not recommendations:
        recommendations.append(
            "Good match! Tailor your resume to the job and "
            "include measurable achievements."
        )

    return {
        "score": score,
        "job_requirements": display_skills(required_skills),
        "found_skills": display_skills(found_skills),
        "missing_skills": display_skills(missing_skills),
        "recommendations": recommendations,
        "total_required_skills": len(required_skills),
        "matched_skills_count": len(found_skills)
    }


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    if "file" not in request.files:
        return jsonify({"error": "No resume file uploaded."}), 400

    file = request.files["file"]

    if not file.filename:
        return jsonify({"error": "Please select a resume."}), 400

    if not file.filename.lower().endswith((".pdf", ".docx")):
        return jsonify({
            "error": "Only PDF and DOCX files are supported."
        }), 400

    try:
        resume_text = extract_text(file)

        if not resume_text:
            return jsonify({
                "error": "Could not extract text from this file."
            }), 400

        job_description = request.form.get("job_description", "")
        results = analyze_resume_text(resume_text, job_description)

        if "error" in results:
            return jsonify(results), 400

        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                INSERT INTO analysis_history
                (filename, score, found_skills, missing_skills)
                VALUES (?, ?, ?, ?)
            """, (
                os.path.basename(file.filename),
                results["score"],
                ", ".join(results["found_skills"]),
                ", ".join(results["missing_skills"])
            ))

        return jsonify(results)

    except Exception as exc:
        app.logger.exception("Resume analysis failed")
        return jsonify({
            "error": "Resume analysis failed. Check that the file is valid."
        }), 500


@app.route("/history", methods=["GET"])
def history():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT id, filename, score, found_skills,
                   missing_skills, created_at
            FROM analysis_history
            ORDER BY id DESC
        """).fetchall()

    return jsonify([dict(row) for row in rows])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
