from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# 각 과목 정원
limits = {
    "베이킹": 3,
    "비즈": 4,
    "모루인형": 3,
    "슈링클": 4,
    "꽃꽃이": 2,
    "뜨개질": 2
}

# 현재 신청 인원
counts = {course: 0 for course in limits}


@app.route("/")
def index():
    return render_template("popup.html", limits=limits, counts=counts)


@app.route("/apply", methods=["POST"])
def apply():
    course = request.json.get("course")
    if course not in limits:
        return jsonify({"status": "error", "message": "잘못된 과목입니다."})

    if counts[course] < limits[course]:
        counts[course] += 1
        return jsonify({"status": "success", "message": "신청 성공!"})
    else:
        return jsonify({"status": "full", "message": "정원이 초과되었습니다."})


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
