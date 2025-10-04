import pandas as pd
import joblib
import json
import os
import sys
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from datetime import datetime


current_dir = os.path.dirname(os.path.abspath(__file__))
app_path = os.path.join(current_dir, "..", "app")
sys.path.insert(0, os.path.abspath(app_path))


from ml_components import CustomEncoder


dataset_path = os.path.join(current_dir, "20 Percent Training Set.csv")
df = pd.read_csv(dataset_path, header=None)
print("✅ Dataset loaded:", df.shape)

y = df.iloc[:, -2].apply(lambda v: 0 if str(v).strip().lower() == "normal" else 1)
X = df.iloc[:, :-2].copy()  


label_counts = y.value_counts()
print("📊 Label distribution:\n", label_counts)


if label_counts.min() / label_counts.max() < 0.1:
    print("⚠️ Warning: Dataset is imbalanced. You may want to apply resampling.")


pipeline = Pipeline([
    ("encoder", CustomEncoder()),
    ("scaler", StandardScaler()),
    ("model", RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        class_weight="balanced"  # Helps with imbalance
    ))
])

# ✅ Train
pipeline.fit(X, y)
accuracy = round(pipeline.score(X, y), 4)

# ✅ Save model
model_path = os.path.join(current_dir, "nids_pipeline.pkl")
joblib.dump(pipeline, model_path)

# ✅ Save metadata
metadata = {
    "model_version": "1.0.1",
    "trained_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "model_type": "RandomForestClassifier",
    "accuracy": accuracy,
    "num_features": X.shape[1],
    "num_samples": X.shape[0],
    "label_distribution": label_counts.to_dict()
}
meta_path = os.path.join(current_dir, "model_meta.json")
with open(meta_path, "w") as f:
    json.dump(metadata, f, indent=4)

print(f"✅ Model trained and saved. Accuracy: {accuracy}")
print(f"📦 Pipeline saved to: {model_path}")
print(f"📝 Metadata saved to: {meta_path}")
