from flask import Flask, render_template, request, send_file
from dotenv import load_dotenv
import os
from utils import (
    extract_text_from_pdf,
    extract_skills,
    calculate_score,
    predict_role,
    smart_feedback,
    generate_graph,
    generate_pdf_report,
    match_resume_with_jd,
    analyze_resume_sections,
)

load_dotenv()

app = Flask(__name__)
latest_result = {}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():

    resume_file = request.files.get("resume")
    jd_file = request.files.get("job_description")

    # ---------------- Resume Validation ---------------- #

    if not resume_file or resume_file.filename == "":
        return "Please upload a resume."

    resume_name = resume_file.filename.lower()

    if resume_name.endswith(".pdf"):
        resume_text = extract_text_from_pdf(resume_file)
    else:
        resume_text = resume_file.read().decode(
            "utf-8",
            errors="ignore"
        )

    if not resume_text.strip():
        return "Unable to read resume."

    # ---------------- Job Description ---------------- #

    jd_text = ""

    if jd_file and jd_file.filename != "":

        jd_name = jd_file.filename.lower()

        if jd_name.endswith(".pdf"):
            jd_text = extract_text_from_pdf(jd_file)
        else:
            jd_text = jd_file.read().decode(
                "utf-8",
                errors="ignore"
            )

    # ---------------- Resume Analysis ---------------- #

    skills = extract_skills(resume_text)

    score = calculate_score(resume_text)

    role = predict_role(resume_text)

    checkpoints = smart_feedback(
        resume_text,
        score,
        skills
    )

    # ---------------- Resume vs JD Match ---------------- #

    match_percentage = None
    matched_skills = []
    missing_skills = []

    if jd_text:

        (
            match_percentage,
            matched_skills,
            missing_skills
        ) = match_resume_with_jd(
            resume_text,
            jd_text
        )
# ---------------- Graph ---------------- #

    graph = generate_graph(resume_text)
    sections = analyze_resume_sections(resume_text)

    global latest_result

    latest_result = {
        "score": score,
        "role": role,
        "skills": skills,
        "match_percentage": match_percentage,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "feedback": checkpoints
    }
    # ---------------- Debug ---------------- #

    print("\n========== ATS REPORT ==========")
    print("ATS Score :", score)
    print("Role :", role)
    print("Skills :", skills)

    if jd_text:
        print("JD Match :", match_percentage)
        print("Matched :", matched_skills)
        print("Missing :", missing_skills)

    print("===============================\n")

    return render_template(
        "result.html",

        score=score,

        role=role,

        skills=skills,

        checkpoints=checkpoints,

        graph=graph,

        match_percentage=match_percentage,

        matched_skills=matched_skills,

        missing_skills=missing_skills,
        sections=sections,
    )
@app.route("/download-report")
def download_report():

    import tempfile

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    temp.close()
    generate_pdf_report(
        temp.name,
        latest_result.get("score", 0),
        latest_result.get("role", ""),
        latest_result.get("skills", []),
        latest_result.get("match_percentage", None),
        latest_result.get("matched_skills", []),
        latest_result.get("missing_skills", []),
        latest_result.get("feedback", [])
    )


    return send_file(
        temp.name,
        as_attachment=True,
        download_name="ATS_Report.pdf"
    )
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)