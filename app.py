import os
import json
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, flash

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY") or 'fallback_secret_key'
REPORTS_DIR = "reports"
ADMIN_SECRET_CODE = os.getenv("ADMIN_SECRET_CODE")

USERS = {
    "admin": {"password": "adminpass", "role": "admin"},
}


def load_reports_by_exam_id(exam_id):
    reports = []
    if not os.path.exists(REPORTS_DIR):
        return reports

    for filename in os.listdir(REPORTS_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(REPORTS_DIR, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # On vérifie que le rapport correspond à l'examen demandé
                    if data.get("exam_id") == exam_id:
                        reports.append(data)
            except Exception as e:
                print(f"Erreur lecture fichier {filename} : {e}")
    return reports


def load_report_by_exam_and_student(exam_id, student_name):
    reports = load_reports_by_exam_id(exam_id)
    for report in reports:
        if report.get("student_name") == student_name:
            return report
    return None


@app.route("/", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        role = request.form.get("role", "user")
        admin_code = request.form.get("admin_code", "")

        if username in USERS:
            flash("Nom d'utilisateur déjà utilisé.", "danger")
            return render_template("register.html")

        if role != "admin":
            flash("Seuls les administrateurs peuvent s'inscrire.", "danger")
            return render_template("register.html")

        if admin_code != ADMIN_SECRET_CODE:
            flash("Code admin incorrect. Inscription refusée.", "danger")
            return render_template("register.html")

        USERS[username] = {"password": password, "role": "admin"}
        flash("Compte administrateur créé avec succès. Connectez-vous !", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = USERS.get(username)
        if user and user["password"] == password and user["role"] == "admin":
            session["username"] = username
            session["role"] = "admin"
            flash("Connexion réussie", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Identifiants invalides ou accès non autorisé", "danger")

    return render_template("login.html")


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if not session.get("username") or session.get("role") != "admin":
        flash("Accès réservé aux administrateurs uniquement", "danger")
        return redirect(url_for("login"))

    if request.method == "POST":
        exam_id = request.form.get("exam_id")
        if exam_id:
            return redirect(url_for("exam", exam_id=exam_id))
        else:
            flash("Veuillez entrer un ID d'examen valide.", "warning")

    return render_template("dashboard.html", role=session.get("role"), username=session.get("username"))


@app.route("/exam/<exam_id>")
def exam(exam_id):
    if not session.get("username") or session.get("role") != "admin":
        return "Accès refusé", 403

    reports = load_reports_by_exam_id(exam_id)
    return render_template("exam.html", exam_id=exam_id, reports=reports)


@app.route("/exam/<exam_id>/student/<student_name>")
def student_detail(exam_id, student_name):
    if not session.get("username") or session.get("role") != "admin":
        return "Accès refusé", 403

    report = load_report_by_exam_and_student(exam_id, student_name)
    if not report:
        return "Rapport non trouvé", 404

    return render_template("student_detail.html", report=report)


@app.route("/logout")
def logout():
    session.clear()
    flash("Déconnecté avec succès", "info")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
