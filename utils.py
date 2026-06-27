from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.colors import blue
import fitz
import base64
import io
import matplotlib.pyplot as plt
import os
# ---------------- Skill Database ---------------- #

KEYWORDS = [
    "python",
    "java",
    "c++",
    "sql",
    "mysql",
    "mongodb",
    "flask",
    "django",
    "html",
    "css",
    "javascript",
    "react",
    "node.js",
    "machine learning",
    "deep learning",
    "nlp",
    "tensorflow",
    "pytorch",
    "opencv",
    "numpy",
    "pandas",
    "scikit-learn",
    "power bi",
    "excel",
    "git",
    "github",
    "docker",
    "aws",
    "linux"
]

# ---------------- PDF ---------------- #

def extract_text_from_pdf(file_storage):
    file_bytes = file_storage.read()

    doc = fitz.open(
        stream=file_bytes,
        filetype="pdf"
    )

    text = ""

    for page in doc:
        text += page.get_text()

    doc.close()

    return text


# ---------------- Skills ---------------- #

def extract_skills(text):

    text = text.lower()

    skills = []

    for skill in KEYWORDS:
        if skill in text:
            skills.append(skill)

    return sorted(list(set(skills)))
# ---------------- ATS Score ---------------- #

def calculate_score(text):

    text = text.lower()
    score = 0

    # ---------------- Contact Details ----------------
    if "@" in text:
        score += 5

    if any(word in text for word in ["phone", "mobile", "+91"]):
        score += 5

    # ---------------- Skills ----------------
    skills = extract_skills(text)

    score += min(len(skills) * 5, 30)

    # ---------------- Projects ----------------
    if "project" in text or "projects" in text:
        score += 20

    # ---------------- Experience ----------------
    if any(word in text for word in [
        "experience",
        "internship",
        "worked",
        "employment"
    ]):
        score += 15

    # ---------------- Education ----------------
    if any(word in text for word in [
        "education",
        "b.e",
        "b.tech",
        "bachelor",
        "master",
        "university",
        "college"
    ]):
        score += 10

    # ---------------- Certifications ----------------
    if any(word in text for word in [
        "certification",
        "certifications",
        "certificate"
    ]):
        score += 10

    # ---------------- Online Profiles ----------------
    if "github" in text:
        score += 3

    if "linkedin" in text:
        score += 2

    return min(score, 100)

# ---------------- Role Prediction ---------------- #

def predict_role(text):

    text = text.lower()

    roles = {

        "ML Engineer": [
            "machine learning",
            "tensorflow",
            "keras",
            "pytorch"
        ],

        "Data Analyst": [
            "sql",
            "excel",
            "power bi",
            "tableau"
        ],

        "Backend Developer": [
            "flask",
            "django",
            "fastapi"
        ],

        "Frontend Developer": [
            "react",
            "javascript",
            "html",
            "css"
        ],

        "AI Engineer": [
            "deep learning",
            "nlp",
            "opencv"
        ]

    }

    scores = {}

    for role, keywords in roles.items():

        scores[role] = 0

        for keyword in keywords:

            if keyword in text:
                scores[role] += 1

    return max(scores, key=scores.get)


# ---------------- Resume Feedback ---------------- #

def smart_feedback(text, score, skills):

    text = text.lower()

    feedback = []

    if score >= 85:
        feedback.append("✅ Excellent ATS Score. Your resume is highly competitive.")

    elif score >= 70:
        feedback.append("✅ Good Resume. Small improvements can increase your ATS score.")

    elif score >= 50:
        feedback.append("⚠ Average Resume. Add more projects and technical skills.")

    else:
        feedback.append("❌ Resume needs significant improvement.")

    if len(skills) < 6:
        feedback.append("⚠ Add more relevant technical skills.")

    if "project" not in text:
        feedback.append("❌ Include at least 2 strong projects.")

    if "experience" not in text and "internship" not in text:
        feedback.append("⚠ Add internship or work experience.")

    if "github" not in text:
        feedback.append("⚠ Add your GitHub profile link.")

    if "linkedin" not in text:
        feedback.append("⚠ Add your LinkedIn profile.")

    if "certification" not in text and "certifications" not in text:
        feedback.append("⚠ Add certifications to strengthen your resume.")

    return feedback


# ---------------- Resume vs JD Matching ---------------- #
import re
def match_resume_with_jd(resume_text, jd_text):

    resume_text = resume_text.lower()
    jd_text = jd_text.lower()

    resume_skills = set()
    jd_skills = set()

    for skill in KEYWORDS:
        if skill in resume_text:
            resume_skills.add(skill)
        if skill in jd_text:
            jd_skills.add(skill)

    matched = sorted(list(resume_skills & jd_skills))
    missing = sorted(list(jd_skills - resume_skills))

    # 🔥 FIXED SCORE LOGIC
    if len(jd_skills) == 0:
        percentage = 0
    else:
        percentage = round((len(matched) / len(jd_skills)) * 100)

    return percentage, matched, missing

# ---------------- Graph ---------------- #

def generate_graph(text):

    skills = extract_skills(text)

    if not skills:

        skills = ["No Skills"]

        values = [1]

    else:

        values = []

        lower_text = text.lower()

        for skill in skills:
            values.append(lower_text.count(skill))

    fig, ax = plt.subplots(figsize=(8,4))

    ax.bar(skills, values)

    ax.set_title("Detected Skills")

    plt.xticks(rotation=45)

    plt.tight_layout()

    buf = io.BytesIO()

    plt.savefig(buf, format="png")

    plt.close(fig)

    buf.seek(0)

    image = base64.b64encode(buf.read()).decode("utf-8")

    return image
def generate_pdf_report(
        filename,
        score,
        role,
        skills,
        match_percentage,
        matched_skills,
        missing_skills,
        feedback):

    styles = getSampleStyleSheet()

    title = styles["Heading1"]
    title.alignment = TA_CENTER
    title.textColor = blue

    heading = styles["Heading2"]

    normal = styles["BodyText"]

    pdf = SimpleDocTemplate(filename)

    story = []

    story.append(Paragraph("AI ATS Resume Analysis Report", title))

    story.append(Paragraph("<br/>", normal))

    story.append(Paragraph(f"<b>ATS Score :</b> {score}/100", heading))

    story.append(Paragraph(f"<b>Predicted Role :</b> {role}", normal))

    if match_percentage is not None:
        story.append(
            Paragraph(
                f"<b>Job Description Match :</b> {match_percentage}%",
                normal
            )
        )

    story.append(Paragraph("<br/>", normal))

    story.append(
        Paragraph(
            "<b>Detected Skills</b>",
            heading
        )
    )

    story.append(
        Paragraph(
            ", ".join(skills) if skills else "No Skills Found",
            normal
        )
    )

    story.append(Paragraph("<br/>", normal))

    if matched_skills:

        story.append(
            Paragraph(
                "<b>Matched Skills</b>",
                heading
            )
        )

        story.append(
            Paragraph(
                ", ".join(matched_skills),
                normal
            )
        )

    story.append(Paragraph("<br/>", normal))

    if missing_skills:

        story.append(
            Paragraph(
                "<b>Missing Skills</b>",
                heading
            )
        )

        story.append(
            Paragraph(
                ", ".join(missing_skills),
                normal
            )
        )

    story.append(Paragraph("<br/>", normal))

    story.append(
        Paragraph(
            "<b>AI Feedback</b>",
            heading
        )
    )

    for item in feedback:

        story.append(
            Paragraph(
                "• " + item,
                normal
            )
        )

    pdf.build(story)

    return filename
def analyze_resume_sections(text):

    text = text.lower()

    sections = {}

    sections["Contact Details"] = (
        "@" in text and
        any(x in text for x in ["phone", "+91", "mobile"])
    )

    sections["Education"] = any(
        x in text
        for x in [
            "education",
            "college",
            "university",
            "b.tech",
            "b.e",
            "degree",
            "master"
        ]
    )

    sections["Projects"] = (
        "project" in text or
        "projects" in text
    )

    sections["Experience"] = any(
        x in text
        for x in [
            "experience",
            "internship",
            "worked"
        ]
    )

    sections["Skills"] = len(extract_skills(text)) > 0

    sections["GitHub"] = "github" in text

    sections["LinkedIn"] = "linkedin" in text

    sections["Certifications"] = any(
        x in text
        for x in [
            "certification",
            "certificate",
            "certifications"
        ]
    )

    return sections
