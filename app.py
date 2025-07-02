from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import json

app = Flask(__name__)
app.secret_key = 'change_this_secret_key'
REPORTS_DIR = "reports"

# Simuler une base d'utilisateurs (à remplacer par une vraie DB en prod)
USERS = {
    "admin": {"password": "adminpass", "role": "admin"},
    "etudiant1": {"password": "userpass", "role": "user"},
}

def load_reports_by_exam_id(exam_id):
    reports = []
    for filename in os.listdir(REPORTS_DIR):
        if filename.endswith(".json") and f"_{exam_id}_" in filename:
            with open(os.path.join(REPORTS_DIR, filename), "r", encoding="utf-8") as f:
                report = json.load(f)
                reports.append(report)
    return reports

# Page de connexion
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = USERS.get(username)
        if user and user["password"] == password:
            session["username"] = username
            session["role"] = user["role"]
            flash("Connexion réussie", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Identifiants invalides", "danger")
    return render_template("login.html")

# Page de déconnexion
@app.route("/logout")
def logout():
    session.clear()
    flash("Déconnecté avec succès", "info")
    return redirect(url_for("login"))

# Accueil après connexion
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if not session.get("username"):
        return redirect(url_for("login"))

    if request.method == "POST":
        exam_id = request.form.get("exam_id")
        return redirect(url_for("exam", exam_id=exam_id))
    return render_template("dashboard.html", role=session.get("role"))

@app.route("/exam/<exam_id>")
def exam(exam_id):
    if not session.get("username"):
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return "Accès refusé. Réservé aux administrateurs.", 403

    reports = load_reports_by_exam_id(exam_id)
    return render_template("exam.html", exam_id=exam_id, reports=reports)

@app.route("/exam/<exam_id>/student/<student_name>")
def student_detail(exam_id, student_name):
    if not session.get("username"):
        return redirect(url_for("login"))

    # Admin : peut tout voir
    # Utilisateur : ne voit que son propre rapport
    if session.get("role") != "admin" and session.get("username") != student_name:
        return "Accès interdit", 403

    reports = load_reports_by_exam_id(exam_id)
    student_report = next((r for r in reports if r["student_name"] == student_name), None)
    if not student_report:
        return f"Étudiant {student_name} non trouvé pour l'examen {exam_id}", 404
    return render_template("student_detail.html", report=student_report)

if __name__ == "__main__":
    app.run(debug=True)
