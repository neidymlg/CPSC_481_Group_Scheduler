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
        if c.get("name") and int(c.get("amount", 0)) > 0 
    ]
    
    if not chores:
        return jsonify({"error": "No chores provided"}), 400

    #map chore names to index/order
    chore_names = [c.name for c in chores]
    chore_index = {name: idx for idx, name in enumerate(chore_names)}

    difficulties = data.get("difficulties", {}) or {}
    loved_payload = data.get("loved", {}) or {}
    hated_payload = data.get("hated", {}) or {}
    users_payload = data.get("users", [])

    users = []
    for u in users_payload:
        name = u.get("name")
        if not name:
            continue
        max_chores = int(u.get("max_chores", 0))

        #build difficulty list aligning with chore order
        user_diff_by_name = difficulties.get(name, {}) or {}
        diff_list = [
            int(user_diff_by_name.get(chore_name, 0))
            for chore_name in chore_names
        ]
        
        #loved/hated chores come from the dropdown UI as names
        loved_names = loved_payload.get(name, []) or []
        hated_names = hated_payload.get(name, []) or []

        loved_indices = [
            chore_index[ch]
            for ch in loved_names
            if ch in chore_index
        ]
        hated_indices = [
            chore_index[ch]
            for ch in hated_names
            if ch in chore_index
        ]

        users.append(User(name, max_chores, difficulty=diff_list, hated_chores=hated_indices, loved_chores=loved_indices,))

    if not users:
        return jsonify({"error": "No users provided"}), 400

    scheduler = Chore_Scheduler(chores, users)

    #added quality metrics in generated schedule with simulated annealing
    best_schedule, best_score = scheduler.simulated_annealing()
    quality = scheduler.accuracy_score(best_schedule)

    return jsonify({
        "schedule": best_schedule,
        "quality": quality,
    })


if __name__ == "__main__":
    app.run(debug=True)