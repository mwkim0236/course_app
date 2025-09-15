from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "secret_key"  # 세션 유지를 위한 키 (임의값)

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
    # 이름이 세션에 없으면 이름 입력 페이지로 이동
    if "name" not in session:
        return redirect(url_for("name_input"))

    name = session["name"]
    # 각 과목의 현재 신청자 수 업데이트
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
    if "name" not in session:
        return redirect(url_for("name_input"))

    name = session["name"]
    my_course = None
    for c, data in courses.items():
        if name in data["students"]:
            my_course = c
            break
    return render_template("my_course.html", name=name, course=my_course)


@app.route("/admin")
def admin():
    course_status = {
        c: {"capacity": data["capacity"], "registered": len(data["students"]), "students": data["students"]}
        for c, data in courses.items()
    }
    return render_template("admin.html", courses=course_status)


@app.route("/admin/delete", methods=["POST"])
def admin_delete():
    course = request.form.get("course")
    student = request.form.get("student")

    if course in courses and student in courses[course]["students"]:
        courses[course]["students"].remove(student)

    return redirect(url_for("admin"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
