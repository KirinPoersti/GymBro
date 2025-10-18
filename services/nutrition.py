from math import isfinite


def to_float(x, default=None):
    try:
        v = float(str(x))
        return v if isfinite(v) else default
    except (ValueError, TypeError):
        return default


def to_int(x, default=None):
    try:
        return int(float(str(x)))
    except (ValueError, TypeError):
        return default


def compute_calories_and_macros(weight_kg, height_cm, age, sex, activity_factor, goal, calorie_plan):
    if None in (weight_kg, height_cm, age) or sex not in ("male", "female") or activity_factor is None:
        return None, None, None, None

    bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + (5 if sex == "male" else -161)
    tdee = round(bmr * activity_factor)

    if calorie_plan == "cut":
        calories = round(tdee * 0.80)
    elif calorie_plan == "bulk":
        calories = round(tdee * 1.10)
    else:
        calories = tdee

    perkg = {"fat_loss": 1.0, "casual": 1.5, "muscle": 2.2}.get(goal, 1.5)
    protein_g = round(perkg * weight_kg)

    calories_after_protein = max(0, calories - protein_g * 4)
    carbs_low_g = round((calories_after_protein * 0.30) / 4)
    carbs_high_g = round((calories_after_protein * 0.60) / 4)

    return calories, protein_g, carbs_low_g, carbs_high_g

