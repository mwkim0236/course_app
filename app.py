from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "secret123"  # 세션 저장용

courses = {
    "베이킹": {"capacity": 3, "students": []},
    "비즈": {"capacity": 4, "students": []},
    "모루인형": {"capacity": 3, "students": []},
    "슈링클": {"capacity": 4, "students": []},
    "꽃꽃이": {"capacity": 2, "students": []},
    "뜨개질": {"capacity": 2, "students": []},
}

# ---------------- 사용자 이름 입력 ----------------
@app.route("/", methods=["GET", "POST"])
def name_input():
    if request.method == "POST":
        username = request.form.get("username")
        if username:
            session["username"] = username
            return redirect(url_for("index"))
    return render_template("name_input.html")

# ---------------- 수강 신청 메인 ----------------
@app.route("/index")
def index():
    if "username" not in session:
        return redirect(url_for("name_input"))
    return render_template("index.html", courses=courses)

# ---------------- 수강 신청 처리 ----------------
@app.route("/apply/<course>")
def apply(course):
    username = session.get("username")
    if not username:
        return redirect(url_for("name_input"))

    if len(courses[course]["students"]) < courses[course]["capacity"]:
        courses[course]["students"].append(username)
        message = f"{course} 신청 성공!"
        success = True
    else:
        message = f"{course} 정원 초과!"
        success = False
    return render_template("popup.html", message=message, success=success)

# ---------------- 내 신청 내역 ----------------
@app.route("/my_courses")
def my_courses():
    username = session.get("username")
    if not username:
        return redirect(url_for("name_input"))

    my_list = [c for c, data in courses.items() if username in data["students"]]
    return render_template("my_courses.html", my_list=my_list)

# ---------------- 관리자 페이지 ----------------
@app.route("/admin")
def admin():
    return render_template("admin.html", courses=courses)

# ---------------- 관리자: 신청자 삭제 ----------------
@app.route("/admin/delete/<course>/<student>", methods=["POST"])
def delete_student(course, student):
    if student in courses[course]["students"]:
        courses[course]["students"].remove(student)
    return redirect(url_for("admin"))

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
