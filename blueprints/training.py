from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, session, abort, jsonify

from services.auth import login_required
from services.workouts import save_workout, fetch_workout_payload


bp = Blueprint("training_bp", __name__)


EXERCISE_GROUPS = {
    "Glutes": [
        "Back Squat","Belt Squat","Box Pistol Squat","Bulgarian Split Squat, Barbell",
        "Bulgarian Split Squat, Dumbbells","Bulgarian Split Squat, Smith Machine",
        "Bulgarian Split Squat 1.5 Reps, Smith Machine","Deadlift","Deficit Deadlift",
        "Deficit Sumo Deadlift","Elevated Goblet Squat","Elevated Goblet Squat 1.5 Reps",
        "Forward Lunge with Barbell, One Leg at a Time","Front Squat","Glute Kickback",
        "Glute Kickback, Machine","Goblet Squat","Hack Squat","Hack Squat, 1.5 Reps",
        "Hip Abduction Machine","Hip Thrust","Hip Thrust Machine","Horizontal Leg Press",
        "Leg Press","Machine Step-Up","Paused Back Squat","Paused Bulgarian Split Squat, Smith Machine",
        "Paused Deadlift","Paused Sumo Deadlift","Pendulum Squat",
        "Reverse Lunge with Barbell, One Leg at a Time","Reverse Super Squat","Romanian Deadlift",
        "Romanian Sumo Deadlift","Safety Bar Squat","Single-Leg Hip Thrust",
        "Single-Leg Machine Hip Thrust","Single-Leg Romanian Deadlift",
        "Single-Leg Romanian Deadlift, Smith Machine","Single-Leg RDL, Kettlebell",
        "Smith Machine Squat","Step-Up","Sumo Deadlift","Trap Bar Deadlift",
        "Vertical Leg Press","Walking Lunges",
    ],
    "Shoulders": [
        "Arnold Press","Barbell Upright Row","Cable Cross Lateral Raise","Cable Lateral Raise",
        "Dumbbell Lateral Raise","Dumbbell Lateral Raise, 1.5 Reps","Dumbbell Lateral Raise, Paused",
        "Dumbbell Shoulder Press","Dumbbell Upright Row","Face Pull","Incline Dumbbell Lateral Raise",
        "Leaning Cable Lateral Raise","Leaning Lateral Raise","Machine Lateral Raise",
        "Machine Shoulder Press","Overhead Press","Rear Delt Machine",
        "Seated Dumbbell Lateral Raise","Seated Dumbbell Shoulder Press",
        "Single Arm Shoulder Press","Smith Machine Overhead Press","Standing Cable Row with Rope",
    ],
    "Quads": [
        "Back Squat","Belt Squat","Box Pistol Squat","Bulgarian Split Squat, Barbell",
        "Bulgarian Split Squat, Dumbbells","Bulgarian Split Squat, Smith Machine",
        "Bulgarian Split Squat 1.5 Reps, Smith Machine","Elevated Goblet Squat",
        "Elevated Goblet Squat, 1.5 Reps","Forward Lunge with Barbell, One Leg at a Time","Front Squat",
        "Goblet Squat","Hack Squat","Hack Squat, 1.5 Reps","Horizontal Leg Press","Leg Extension","Leg Press",
        "Machine Step-Up","Paused Back Squat","Paused Bulgarian Split Squat, Smith Machine","Pendulum Squat",
        "Reverse Lunge with Barbell, One Leg at a Time","Reverse Super Squat","Safety Bar Squat",
        "Single Leg Extension","Single Leg Press","Smith Machine Squat","Step-Up","Vertical Leg Press","Walking Lunges",
    ],
    "Chest": [
        "Barbell Bench Press","Barbell Bench Press 1.5 Reps","Barbell Bench Press with Pause",
        "Cable Chest Fly, Downward","Cable Chest Fly, Forward","Cable Chest Fly, Low to High",
        "Chest Fly Machine","Chest Fly Machine, 1.5 Reps","Chest Press Machine",
        "Close Grip Bench Press","Decline Push-Ups","Dips","Dumbbell Bench Press",
        "Dumbbell Bench Press, Paused","Incline Dumbbell Bench Press",
        "Incline Dumbbell Bench Press 1.5 Reps","Incline Dumbbell Fly","Incline Press Machine",
        "Kneeling Push-Up","Machine Assisted Dip","Push-Ups","Smith Machine Incline Bench Press",
    ],
    "Hamstrings": [
        "Back Extension","Bar Extension Machine","Deadlift","Deficit Deadlift","Deficit Sumo Deadlift",
        "Good Morning","Hip Adduction Machine","Lying Leg Curl","Romanian Deadlift",
        "Romanian Sumo Deadlift","Seated Leg Curl","Single-Leg Lying Leg Curl",
        "Single-Leg Romanian Deadlift","Single-Leg Romanian Deadlift, Smith Machine",
        "Single-Leg Romanian Deadlift, Trap Bar","Single-Leg RDL, Kettlebell",
        "Single-Leg Seated Leg Curl","Sumo Deadlift","Sumo Deadlift, Paused","Trap Bar Deadlift",
    ],
    "Triceps": [
        "Cable Tricep Kickback","Incline Tricep Extension, Dumbbell","JM Press",
        "Lying Barbell Tricep Extension","Lying Tricep Extension, Dumbbell","Machine Tricep Extension",
        "Overhead Barbell Tricep Extension","Overhead Cable Tricep Extension, Bar",
        "Overhead Cable Tricep Extension, Rope","Single Arm Tricep Extension, Dumbbell",
        "Triceps Pushdown, Rope","Triceps Pushdown, Straight Bar",
    ],
    "Calves": [
        "Horizontal Calf Press","Horizontal Calf Press Machine","Leg Press Calf Raise",
        "Seated Calf Raise","Smith Machine Calf Raise","Standing Calf Machine",
    ],
    "Biceps": [
        "21s (21 Shot)","Barbell Curl","Barbell Reverse Curl","Bayesian Cable Curl",
        "Cable Bicep Curl","Concentration Curl","Dumbbell Biceps Curl",
        "Dumbbell Preacher Curl","Hammer Curl","Incline Dumbbell Curl","Incline Hammer Curl",
        "Machine Biceps Curl","Preacher Curl",
    ],
    "Abs": [
        "Ab Rotations, Machine","Ab Wheel","Cable Crunch","Cable Oblique Twist",
        "Cable Oblique Twist, High-to-Low","Hanging Knee Raise","Hanging Leg Raise to 90 Degrees",
        "Hanging Leg Raises","Hanging Windshield Wipers","Incline Bench Sit-Up","Knee Raise, Supported",
        "Knee-Supported Ab Rotation, Machine","Leg Raises, Supported","Lying Leg Raises",
        "Pallof Press","Seated Machine Crunch","V Sit-Up","Weighted Ab Rotation",
    ],
    "Back": [
        "Band Assisted Chin-Up","Barbell Bent Over Row, Overhand Grip",
        "Barbell Bent Over Row, Smith Machine","Barbell Bent Over Row, Underhand Grip","Barbell Shrug",
        "Cable Lat Pullover","Cable Lat Pullover 1.5 Reps","Chest-Supported T-Bar Row","Chin-Ups","High Row",
        "Lat Pulldown, Neutral Grip","Lat Pulldown, Underhand Grip","Low Row","Machine Chest Supported Row",
        "Machine Chin-Up","Neutral Grip Chin-Up","Pull-Ups","Seal Row, Overhand Grip","Seal Row, Underhand Grip",
        "Seated Cable Row","Seated Cable Row, Overhand Grip","Single-Arm Chest-Supported Row, Machine",
        "Single-Arm Dumbbell Row","Single-Arm Lat Pulldown","Single-Arm Seated Cable Row","T-Bar Row",
    ],
}
EXERCISE_CATALOG = [name for group in EXERCISE_GROUPS.values() for name in group]


@bp.route("/day/<d>/training", methods=["GET", "POST"], endpoint="training")
@login_required
def training(d: str):
    try:
        y, m, dd = (int(x) for x in d.split("-"))
        _ = date(y, m, dd)
    except Exception:
        abort(404)

    uid = session["user_id"]

    if request.method == "POST":
        # Legacy JSON submission
        data = request.get_json(silent=True)
        if data is not None:
            exercises = data.get("exercises", [])
            try:
                save_workout(uid, d, exercises)
            except ValueError:
                return (jsonify({"ok": False, "error": "invalid_user"}), 401)
            return jsonify({"ok": True})

        # No-JS form submission
        ex_names = request.form.getlist("ex_name[]")
        ex_groups = request.form.getlist("ex_group[]")
        exercises_state = []
        for i, nm in enumerate(ex_names):
            sets = []
            w_list = request.form.getlist(f"set_weight_{i}[]")
            r_list = request.form.getlist(f"set_reps_{i}[]")
            max_len = max(len(w_list), len(r_list)) if (w_list or r_list) else 0
            for j in range(max_len):
                sets.append({
                    "weight": (w_list[j] if j < len(w_list) else ""),
                    "reps": (r_list[j] if j < len(r_list) else ""),
                })
            exercises_state.append({
                "name": nm,
                "group": (ex_groups[i] if i < len(ex_groups) else "All"),
                "sets": sets,
            })

        # Handle UI actions
        if "add_ex" in request.form:
            exercises_state.append({"name": "", "group": "All", "sets": []})
            return render_template("training.html", d=d, exercises=exercises_state)
        if "remove_ex" in request.form:
            try:
                ridx = int(request.form.get("remove_ex"))
            except Exception:
                ridx = -1
            if 0 <= ridx < len(exercises_state):
                del exercises_state[ridx]
            if not exercises_state:
                exercises_state = [{"name": "", "group": "All", "sets": []}]
            return render_template("training.html", d=d, exercises=exercises_state)
        if "add_set" in request.form:
            try:
                i = int(request.form.get("add_set"))
            except Exception:
                i = -1
            if 0 <= i < len(exercises_state):
                exercises_state[i]["sets"].append({"weight": "", "reps": ""})
            return render_template("training.html", d=d, exercises=exercises_state)
        if "remove_set" in request.form:
            raw = request.form.get("remove_set", "")
            try:
                i_s, j_s = raw.split("-", 1)
                i, j = int(i_s), int(j_s)
            except Exception:
                i, j = -1, -1
            if 0 <= i < len(exercises_state) and 0 <= j < len(exercises_state[i]["sets"]):
                del exercises_state[i]["sets"][j]
            return render_template("training.html", d=d, exercises=exercises_state)

        # Save
        try:
            save_workout(uid, d, exercises_state)
        except ValueError:
            abort(401)
        return redirect(url_for("training_bp.training", d=d), code=303)

    exercises_payload = fetch_workout_payload(uid, d)
    return render_template("training.html", d=d, exercises=exercises_payload)


@bp.get("/api/exercises", endpoint="api_exercises")
@login_required
def api_exercises():
    q = (request.args.get("q") or "").strip().lower()
    group = (request.args.get("group") or "All").strip()

    if group and group != "All" and group in EXERCISE_GROUPS:
        source = EXERCISE_GROUPS[group]
    else:
        source = EXERCISE_CATALOG

    if not q:
        starter = sorted(source)[:50]
        return jsonify(starter)

    scored = []
    for name in source:
        ln = name.lower()
        if q in ln:
            scored.append(((ln.find(q), len(ln)), name))
    scored.sort(key=lambda t: t[0])

    return jsonify([name for _, name in scored[:50]])

