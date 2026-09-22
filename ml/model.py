import os
import joblib
import pandas as pd

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "wait_time_model.pkl"
)


# -----------------------------------------
# Load trained model
# -----------------------------------------
def load_model():
    if not os.path.exists(MODEL_PATH):
        return None

    return joblib.load(MODEL_PATH)


# -----------------------------------------
# Predict restaurant waiting time
# -----------------------------------------
def predict_wait_time(
    people_inside,
    total_tables,
    occupied_tables,
    people_entered,
    people_left,
    average_stay_minutes
):
    model = load_model()

    # -----------------------------------------
    # AI model prediction
    # -----------------------------------------
    if model is not None:
        input_data = pd.DataFrame([{
            "people_inside": people_inside,
            "total_tables": total_tables,
            "occupied_tables": occupied_tables,
            "people_entered": people_entered,
            "people_left": people_left,
            "average_stay_minutes": average_stay_minutes
        }])

        prediction = model.predict(input_data)
        wait_time = float(prediction[0])

    # -----------------------------------------
    # Backup rule if model is unavailable
    # -----------------------------------------
    else:
        occupancy_ratio = (
            occupied_tables / total_tables
            if total_tables > 0
            else 0
        )

        crowd_pressure = (
            people_inside * 0.8
            + people_entered * 1.2
            - people_left * 0.7
        )

        wait_time = (
            occupancy_ratio * average_stay_minutes
            + crowd_pressure * 0.15
            - 8
        )

    # Keep prediction sensible
    wait_time = max(0, wait_time)
    wait_time = min(wait_time, 120)

    return round(wait_time, 1)


# -----------------------------------------
# Crowd level
# -----------------------------------------
def get_crowd_level(
    people_inside,
    total_tables,
    occupied_tables
):
    if total_tables <= 0:
        return "Unknown"

    occupancy = occupied_tables / total_tables

    if occupancy < 0.40:
        return "Low"
    elif occupancy < 0.70:
        return "Moderate"
    elif occupancy < 0.90:
        return "Busy"
    else:
        return "Very Busy"


# -----------------------------------------
# Customer recommendation
# -----------------------------------------
def get_recommendation(
    wait_time,
    available_tables,
    people_inside,
    total_tables
):
    if available_tables >= 3 and wait_time <= 10:
        return {
            "label": "GO NOW",
            "class": "go",
            "icon": "🟢",
            "message": "Good time to visit. Tables are available."
        }
    elif available_tables >= 1 and wait_time <= 20:
        return {
            "label": "WAIT A LITTLE",
            "class": "wait",
            "icon": "🟡",
            "message": "Moderate crowd. You may want to wait a little."
        }
    else:
        return {
            "label": "VERY BUSY",
            "class": "busy",
            "icon": "🔴",
            "message": "The restaurant is currently crowded."
        }