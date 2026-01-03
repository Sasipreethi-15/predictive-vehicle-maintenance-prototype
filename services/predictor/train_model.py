import sqlite3
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib

# Connect to database
conn = sqlite3.connect("database/vehicle_data.db")

# Load data
df = pd.read_sql("SELECT * FROM vehicle_telemetry", conn)

# Simple labeling logic
# If engine_temp > 100 OR rpm > 3000 → Fault (1)
# Else → Normal (0)
df["label"] = df.apply(
    lambda x: 1 if (x["engine_temp"] > 100 or x["rpm"] > 3000) else 0,
    axis=1
)

# Features (inputs) & label (output)
X = df[["engine_temp", "rpm", "speed", "coolant_level", "battery_voltage"]]
y = df["label"]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate model
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))

# Save trained model
joblib.dump(model, "services/predictor/fault_prediction_model.pkl")

print("Model trained and saved successfully!")
