import pandas as pd
import joblib


pipeline = joblib.load("ids_project/model/nids_pipeline.pkl")

df = pd.read_csv("test_data.csv") 


if df.shape[1] == 43:
    df = df.iloc[:, :-1]


preds = pipeline.predict(df)
print(preds[:10])  
