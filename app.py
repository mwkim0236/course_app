from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import os

app = Flask(__name__)

# Render 환경변수에서 DB URL 가져오기
DATABASE_URL = os.environ.get("DATABASE_URL")

# 과목별 정원
COURSES = {
    "베이킹": 3,
    "비즈": 4,
    "모루인형": 3,
    "슈링클": 4,
    "꽃꽃이": 2,
    "뜨개질": 2,
}

# ---------------- DB 연결 ----------------
def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            course TEXT NOT NULL
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

# ---------------- 라우트 ----------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["POST"])
def register():
    name = request.form.get("name")
    course = request.form.get("course")

    conn = get_db_connection()
    cur = conn.cursor()

    # 이미 다른 과목 신청했는지 확인
    cur.execute("SELECT course FROM applications WHERE name=%s", (name,))
    existing = cur.fetchone()
    if existing:
        cur.close()
        conn.close()
        return render_template("popup.html", message=f"{name} 님은 이미 [{existing[0]}] 과목을 신청했습니다.", success=False, show_retry=False)

    # 정원 확인
    cur.execute("SELECT COUNT(*) FROM applications WHERE course=%s", (course,))
    count = cur.fetchone()[0]
    if count >= COURSES[course]:
        cur.close()
        conn.close()
        return render_template("popup.html", message=f"[{course}] 과목 정원이 초과되었습니다.", success=False, show_retry=True)

    # 신청 등록
    cur.execute("INSERT INTO applications (name, course) VALUES (%s, %s)", (name, course))
    conn.commit()

    cur.close()
    conn.close()

    return render_template("popup.html", message=f"{name} 님, [{course}] 과목 신청 성공!", success=True)

@app.route("/my_applications", methods=["POST"])
def my_applications():
    name = request.form.get("name")

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT course FROM applications WHERE name=%s", (name,))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    if rows:
        courses = [row[0] for row in rows]
        return render_template("popup.html", message=f"{name} 님 신청 과목: {', '.join(courses)}", success=True)
    else:
        return render_template("popup.html", message=f"{name} 님은 신청 내역이 없습니다.", success=False, show_retry=False)

@app.route("/admin")
def admin():
    conn = get_db_connection()
    cur = conn.cursor()

    courses_data = {}
    for course, capacity in COURSES.items():
        cur.execute("SELECT name FROM applications WHERE course=%s", (course,))
        students = [row[0] for row in cur.fetchall()]
        courses_data[course] = {"capacity": capacity, "students": students}

    cur.close()
    conn.close()

    return render_template("admin.html", courses=courses_data)

@app.route("/admin/delete", methods=["POST"])
def admin_delete():
    name = request.form.get("name")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM applications WHERE name=%s", (name,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("admin"))

# ---------------- 실행 ----------------
if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
