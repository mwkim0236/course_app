from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "secret_key"  # 세션 유지를 위한 키 (임의값)

# 관리자 비밀번호 (배포할 땐 환경변수로 설정하는 게 안전함)
ADMIN_PASSWORD = "admin123"

# 과목별 정원과 신청자 현황
courses = {
    "베이킹": {"capacity": 3, "students": []},
    "비즈": {"capacity": 4, "students": []},
    "모루인형": {"capacity": 3, "students": []},
    "슈링클": {"capacity": 4, "students": []},
    "꽃꽃이": {"capacity": 2, "students": []},
    "뜨개질": {"capacity": 2, "students": []},
}


@app.route("/")
def home():
    if "name" not in session:
        return redirect(url_for("name_input"))

    name = session["name"]
    course_status = {
        c: {"capacity": data["capacity"], "registered": len(data["students"]), "students": data["students"]}
        for c, data in courses.items()
    }
    return render_template("index.html", name=name, courses=course_status)


@app.route("/name_input")
def name_input():
    return render_template("name_input.html")


@app.route("/set_name", methods=["POST"])
def set_name():
    name = request.form.get("name")
    if name:
        session["name"] = name
    return redirect(url_for("home"))


@app.route("/apply", methods=["POST"])
def apply():
    if "name" not in session:
        return redirect(url_for("name_input"))

    name = session["name"]
    course = request.form.get("course")

    # 이미 신청한 과목이 있으면 중복 신청 불가
    for c, data in courses.items():
        if name in data["students"]:
            return render_template("popup.html", message="이미 과목을 신청했습니다.", retry=False)

    # 정원 확인
    if len(courses[course]["students"]) >= courses[course]["capacity"]:
        return render_template("popup.html", message="정원이 초과되었습니다.", retry=True)

    # 수강신청 처리
    courses[course]["students"].append(name)
    return render_template("popup.html", message="신청 성공!", retry=False)


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


# ----------- 관리자 기능 ------------
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        password = request.form.get("password")
        if password == ADMIN_PASSWORD:
            session["is_admin"] = True
            return redirect(url_for("admin"))
        else:
            return render_template("popup.html", message="비밀번호가 틀렸습니다.", retry=True)
    return render_template("admin_login.html")


@app.route("/admin")
def admin():
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))

    course_status = {
        c: {"capacity": data["capacity"], "registered": len(data["students"]), "students": data["students"]}
        for c, data in courses.items()
    }
    return render_template("admin.html", courses=course_status)


@app.route("/admin/delete", methods=["POST"])
def admin_delete():
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))

    course = request.form.get("course")
    student = request.form.get("student")

    if course in courses and student in courses[course]["students"]:
        courses[course]["students"].remove(student)

    return redirect(url_for("admin"))


@app.route("/admin_logout")
def admin_logout():
    session.pop("is_admin", None)
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

