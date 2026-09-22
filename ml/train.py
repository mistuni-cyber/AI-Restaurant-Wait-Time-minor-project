import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

import joblib


# =========================================================
# LOAD DATA
# =========================================================

data = pd.read_csv(
    "ml/training_data.csv"
)


# =========================================================
# FEATURES
# =========================================================

X = data[
    [
        "people_inside",
        "total_tables",
        "occupied_tables",
        "people_entered",
        "people_left",
        "average_stay_minutes"
    ]
]


# =========================================================
# TARGET
# =========================================================

y = data["wait_time"]


# =========================================================
# TRAIN / TEST SPLIT
# =========================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)


# =========================================================
# RANDOM FOREST MODEL
# =========================================================

model = RandomForestRegressor(
    n_estimators=200,
    random_state=42,
    max_depth=8
)


# =========================================================
# TRAIN MODEL
# =========================================================

model.fit(
    X_train,
    y_train
)


# =========================================================
# TEST MODEL
# =========================================================

predictions = model.predict(
    X_test
)


error = mean_absolute_error(
    y_test,
    predictions
)


print()
print("===================================")
print(" AI WAIT TIME MODEL")
print("===================================")

print(
    "Model trained successfully!"
)

print(
    "Average prediction error:",
    round(error, 2),
    "minutes"
)


# =========================================================
# SAVE MODEL
# =========================================================

joblib.dump(
    model,
    "ml/wait_time_model.pkl"
)


print(
    "Model saved successfully!"
)

print("===================================")