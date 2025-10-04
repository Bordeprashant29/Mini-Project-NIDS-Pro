from flask import Blueprint, render_template, request, url_for, current_app, redirect, session, flash
import pandas as pd
import os
import joblib

dash_bp = Blueprint("dash", __name__)

@dash_bp.route("/", methods=["GET", "POST"])
def home():
    if 'user' not in session:
        flash("Please log in to access the dashboard.", "error")
        return redirect(url_for('auth.login'))

    if request.method == "POST":
        file = request.files.get("file")
        if not file or not file.filename.endswith(".csv"):
            flash("Please upload a valid CSV file.", "error")
            return redirect(url_for("dash.home"))

        try:
            # ✅ Load model
            model_path = os.path.join(current_app.root_path, "..", "model", "nids_pipeline.pkl")
            pipeline = joblib.load(model_path)

            # ✅ Read CSV
            df = pd.read_csv(file)

            # ✅ Remove duplicated header row if needed
            if df.columns.tolist() == df.iloc[0].tolist():
                df = df[1:]

            df.reset_index(drop=True, inplace=True)

            # ✅ If 43 columns, assume last is 'count', second last is label -> drop both
            if df.shape[1] == 43:
                df = df.iloc[:, :-2]

            # ✅ If 42 columns, assume last is label -> drop it
            elif df.shape[1] == 42:
                df = df.iloc[:, :-1]

            # ✅ Ensure exactly 41 features now
            if df.shape[1] != 41:
                flash(f"Expected 41 features after cleaning, but got {df.shape[1]}. Please check your CSV.", "error")
                return redirect(url_for("dash.home"))

            # ✅ Remove column headers (some datasets may include them)
            df.columns = list(range(41))

            # ✅ Predict
            preds = pipeline.predict(df)
            df["Prediction"] = ["Normal" if p == 0 else "Attack" for p in preds]

            # ✅ Save output file
            static_folder = os.path.join(current_app.root_path, "static")
            os.makedirs(static_folder, exist_ok=True)
            output_path = os.path.join(static_folder, "predicted_output.csv")
            df.to_csv(output_path, index=False)

            # ✅ Display preview
            display = df.iloc[:, :5].copy()
            display["Prediction"] = df["Prediction"]

            attack_count = (df["Prediction"] == "Attack").sum()
            total = len(df)

            flash(f"Prediction complete. {attack_count} attacks found in {total} records.", "success")
            return render_template(
                "result.html",
                tables=[display.to_html(classes="table table-striped", index=False)],
                download_link=url_for("static", filename="predicted_output.csv"),
                total=total,
                attacks=attack_count
            )

        except Exception as e:
            flash(f"Processing error: {e}", "error")
            return redirect(url_for("dash.home"))

    return render_template("dashboard.html")
