from flask import Flask, render_template, request
from pypdf import PdfReader
from docx import Document
import os
import re

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def extract_text_from_pdf(filepath):
    text = ""

    reader = PdfReader(filepath)

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


def extract_text_from_docx(filepath):
    document = Document(filepath)

    text = ""

    for paragraph in document.paragraphs:
        text += paragraph.text + "\n"

    return text


def extract_information(text):

    # Email
    email_match = re.search(
        r'[\w\.-]+@[\w\.-]+\.\w+',
        text
    )

    email = email_match.group(0) if email_match else "Not found"

    # Phone number
    phone_match = re.search(
        r'(\+91[\s-]?)?[6-9]\d{9}',
        text
    )

    phone = phone_match.group(0) if phone_match else "Not found"

    # Name
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    name = lines[0] if lines else "Not found"

    # Skills
    possible_skills = [
        "Python",
        "Java",
        "C",
        "C++",
        "JavaScript",
        "HTML",
        "CSS",
        "SQL",
        "Machine Learning",
        "Deep Learning",
        "Flask",
        "Django",
        "Git",
        "GitHub",
        "Docker",
        "Jenkins"
    ]

    found_skills = []

    for skill in possible_skills:
        if skill.lower() in text.lower():
            found_skills.append(skill)

    # Education
    education_keywords = [
        "B.Tech",
        "BTech",
        "Bachelor",
        "M.Tech",
        "MTech",
        "MBA",
        "B.Sc",
        "BSc",
        "M.Sc",
        "MSc"
    ]

    education = []

    for item in education_keywords:
        if item.lower() in text.lower():
            education.append(item)

    # Experience
    experience_match = re.search(
        r'(\d+)\+?\s*(years?|yrs?)\s*(of)?\s*experience',
        text,
        re.IGNORECASE
    )

    if experience_match:
        experience = experience_match.group(0)
    else:
        experience = "Not found"

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "skills": found_skills,
        "education": education,
        "experience": experience
    }


@app.route("/")
def home():
    return render_template("upload.html")


@app.route("/upload", methods=["POST"])
def upload():

    if "resume" not in request.files:
        return "No resume selected"

    file = request.files["resume"]

    if file.filename == "":
        return "No resume selected"

    filename = file.filename

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    file.save(filepath)

    extension = filename.lower().split(".")[-1]

    if extension == "pdf":
        text = extract_text_from_pdf(filepath)

    elif extension == "docx":
        text = extract_text_from_docx(filepath)

    else:
        return "Please upload a PDF or DOCX file."

    information = extract_information(text)

    return render_template(
        "result.html",
        information=information
    )


if __name__ == "__main__":
    app.run(debug=True, port=5001)