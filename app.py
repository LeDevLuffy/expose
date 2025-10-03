from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)

SECTIONS_FILE = "sections.json"
QUESTIONS_FILE = "questions.json"
ADMIN_PASSWORD = "Pixiedodo37"  # Change ce mot de passe

# ------------------ Fonctions utilitaires ------------------
def load_json(file):
    if not os.path.exists(file):
        with open(file,"w") as f:
            json.dump([],f)
    with open(file,"r") as f:
        return json.load(f)

def save_json(file, data):
    with open(file,"w") as f:
        json.dump(data, f, indent=4)

# ------------------ Pages élèves ------------------
@app.route("/")
def index():
    sections = load_json(SECTIONS_FILE)
    questions = load_json(QUESTIONS_FILE)
    visible_sections = [s for s in sections if s.get("visible", False)]
    return render_template("index.html", sections=visible_sections, questions=questions)

@app.route("/ask_question", methods=["POST"])
def ask_question():
    questions = load_json(QUESTIONS_FILE)
    question_text = request.form.get("question", "").strip()
    if question_text:
        new_id = max([q["id"] for q in questions]+[0]) + 1
        questions.append({"id": new_id, "text": question_text, "answered": False})
        save_json(QUESTIONS_FILE, questions)
    return redirect(url_for("index"))

@app.route("/like_section/<int:section_id>", methods=["POST"])
def like_section(section_id):
    sections = load_json(SECTIONS_FILE)
    for s in sections:
        if s["id"] == section_id:
            s["likes"] = s.get("likes",0)+1
            break
    save_json(SECTIONS_FILE, sections)
    return redirect(url_for("index"))

# ------------------ Panel admin ------------------
@app.route("/admin", methods=["GET","POST"])
def admin():
    if request.method=="POST":
        password = request.form.get("password","")
        if password != ADMIN_PASSWORD:
            return "Mot de passe incorrect",403
        return redirect(url_for("admin_panel"))
    return render_template("admin.html", auth=False)

@app.route("/admin/panel")
def admin_panel():
    sections = load_json(SECTIONS_FILE)
    questions = load_json(QUESTIONS_FILE)
    return render_template("admin.html", auth=True, sections=sections, questions=questions)

@app.route("/admin/add_section", methods=["POST"])
def add_section():
    sections = load_json(SECTIONS_FILE)
    new_id = max([s["id"] for s in sections]+[0])+1
    title = request.form.get("title")
    type_ = request.form.get("type")
    content = request.form.get("content")
    visible = request.form.get("visible")=="on"
    sections.append({
        "id":new_id,
        "title":title,
        "type":type_,
        "content":content,
        "visible":visible
    })
    save_json(SECTIONS_FILE, sections)
    return redirect(url_for("admin_panel"))

@app.route("/admin/toggle_visibility/<int:section_id>")
def toggle_visibility(section_id):
    sections = load_json(SECTIONS_FILE)
    for s in sections:
        if s["id"] == section_id:
            s["visible"] = not s.get("visible",False)
            break
    save_json(SECTIONS_FILE, sections)
    return redirect(url_for("admin_panel"))

@app.route("/admin/mark_answered/<int:question_id>")
def mark_answered(question_id):
    questions = load_json(QUESTIONS_FILE)
    for q in questions:
        if q["id"]==question_id:
            q["answered"] = not q["answered"]
            break
    save_json(QUESTIONS_FILE, questions)
    return redirect(url_for("admin_panel"))

# ------------------ Adaptation Render ------------------
if __name__=="__main__":
    port = int(os.environ.get("PORT", 5000))  # Utilise le port fourni par Render
    app.run(host="0.0.0.0", port=port, debug=True)
