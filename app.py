from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"

# 관리자 비밀번호
ADMIN_PASSWORD = "admin123"

# 과목 정보 (정원)
COURSES = {
    "베이킹": 3,
    "비즈": 4,
    "모루인형": 3,
    "슈링클": 4,
    "꽃꽃이": 2,
    "뜨개질": 2
}

# -----------------------------
# DB 초기화 함수
# -----------------------------
def init_db():
    conn = sqlite3.connect("applications.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            course TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# -----------------------------
# 라우트
# -----------------------------

@app.route("/")
def name_input():
    return render_template("name_input.html")

@app.route("/set_name", methods=["POST"])
def set_name():
    username = request.form.get("username")
    if not username:
        flash("이름을 입력해주세요.")
        return redirect(url_for("name_input"))
    session["username"] = username
    return redirect(url_for("index"))

@app.route("/index")
def index():
    if "username" not in session:
        return redirect(url_for("name_input"))
    return render_template("index.html", courses=COURSES)

@app.route("/apply/<course>")
def apply(course):
    if "username" not in session:
        return redirect(url_for("name_input"))
    username = session["username"]

    conn = sqlite3.connect("applications.db")
    c = conn.cursor()

    # 이미 신청한 과목이 있는지 확인
    c.execute("SELECT course FROM applications WHERE username = ?", (username,))
    existing = c.fetchone()
    if existing:
        conn.close()
        return render_template("popup.html", message=f"이미 '{existing[0]}' 과목을 신청했습니다.", success=False)

    # 현재 과목 신청 인원 확인
    c.execute("SELECT COUNT(*) FROM applications WHERE course = ?", (course,))
    count = c.fetchone()[0]

    if count >= COURSES[course]:
        conn.close()
        return render_template("popup.html", message=f"'{course}' 과목 정원이 초과되었습니다.", success=False)

    # 신청 저장
    c.execute("INSERT INTO applications (username, course) VALUES (?, ?)", (username, course))
    conn.commit()
    conn.close()

    return render_template("popup.html", message=f"'{course}' 신청 성공!", success=True)

@app.route("/my_course")
def my_course():
    username = session.get("username")
    if not username:
        flash("먼저 이름을 입력해야 합니다.")
        return redirect(url_for("name_input"))

    conn = sqlite3.connect("applications.db")
    c = conn.cursor()
    c.execute("SELECT course FROM applications WHERE username = ?", (username,))
    applications = c.fetchall()
    conn.close()

    return render_template("my_course.html", username=username, applications=applications)

# -----------------------------
# 관리자 페이지
# -----------------------------
@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        password = request.form.get("password")
        if password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            flash("비밀번호가 올바르지 않습니다.")
            return redirect(url_for("admin_login"))
    return render_template("admin_login.html")

@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    conn = sqlite3.connect("applications.db")
    c = conn.cursor()
    c.execute("SELECT id, username, course FROM applications")
    applicants = c.fetchall()
    conn.close()

    return render_template("admin_dashboard.html", applicants=applicants)

@app.route("/admin/delete/<int:applicant_id>")
def admin_delete(applicant_id):
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    conn = sqlite3.connect("applications.db")
    c = conn.cursor()
    c.execute("DELETE FROM applications WHERE id = ?", (applicant_id,))
    conn.commit()
    conn.close()

    flash("신청자가 삭제되었습니다.")
    return redirect(url_for("admin_dashboard"))

# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
