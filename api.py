from flask import Flask, request, jsonify
from Group_Chore_Scheduler import Chore, User, Chore_Scheduler  
app = Flask(
    __name__,
    static_folder="static",
    static_url_path=""  # <-- THIS makes /script.js and /style.css work
)

@app.get("/")
def index():
    # Serve index.html from the static folder
    return app.send_static_file("index.html")

6
@app.post("/schedule")
def make_schedule():
    data = request.get_json(force=True)

    chores = [
        Chore(c["name"], int(c["amount"]))
        for c in data.get("chores", [])
        if c.get("name")
    ]

    users = [
        User(u["name"], int(u["max_chores"]))
        for u in data.get("users", [])
        if u.get("name")
    ]

    scheduler = Chore_Scheduler(chores, users)

    #added quality metrics in generated schedule
    quality = scheduler.accuracy_score(scheduler.schedule)

    return jsonify({
        "schedule": scheduler.schedule,
        "quality": quality,
    })


if __name__ == "__main__":
    app.run(debug=True)